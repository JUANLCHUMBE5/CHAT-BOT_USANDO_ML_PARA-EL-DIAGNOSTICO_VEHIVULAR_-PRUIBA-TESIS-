import time
import requests
from fastapi import APIRouter, Request, Query, HTTPException, BackgroundTasks
from fastapi.responses import PlainTextResponse, JSONResponse
from fastapi.concurrency import run_in_threadpool
from src.core.gestor_diagnostico import GestorDiagnostico
from src.core.logger import logger
from src.config import settings

# Crear enrutador FastAPI para Webhook
router = APIRouter()

# Instanciar el orquestador core de diagnóstico
gestor = GestorDiagnostico()

@router.get("")
def verificar_webhook(
    mode: str = Query(None, alias="hub.mode"),
    token: str = Query(None, alias="hub.verify_token"),
    challenge: str = Query(None, alias="hub.challenge")
):
    """Verificación obligatoria del Webhook requerida por los servidores de Meta Cloud API."""
    if mode == "subscribe" and token == settings.VERIFY_TOKEN:
        logger.info("Webhook de WhatsApp verificado con éxito por Meta.")
        return PlainTextResponse(content=challenge)
    logger.warning("Intento de verificación de Webhook fallido por token incorrecto.")
    raise HTTPException(status_code=403, detail="Verify token incorrecto.")

async def _procesar_y_responder_whatsapp(
    remitente: str, 
    tipo_mensaje: str, 
    texto_cliente: str = "", 
    audio_id: str = "",
    placa: str = "WAPP-01",
    marca_modelo: str = "Vehiculo Generico",
    session_id: str = None
):
    """Procesa en segundo plano la consulta del vehículo y responde vía WhatsApp (Meta / Twilio)."""
    start_t = time.time()
    try:
        id_sesion = session_id or remitente
        if tipo_mensaje == "text":
            respuesta = await run_in_threadpool(
                gestor.procesar_consulta_texto,
                texto_cliente, 
                placa=placa, 
                marca_modelo=marca_modelo, 
                session_id=id_sesion
            )
        elif tipo_mensaje == "audio":
            respuesta = await run_in_threadpool(gestor.procesar_consulta_audio, audio_id)
        else:
            respuesta = "Lo siento, actualmente solo puedo procesar mensajes de texto y notas de audio."

        # Enviar mensaje de respuesta a la Graph API de Meta si hay número válido
        if remitente and not remitente.startswith("test") and settings.TOKEN_WHATSAPP:
            await run_in_threadpool(enviar_mensaje_whatsapp, remitente, respuesta)

        elapsed = (time.time() - start_t) * 1000
        logger.info(f"[Background Task Webhook] Procesado y registrado con éxito en {elapsed:.2f} ms para {remitente}")
    except Exception as e:
        logger.error(f"[Background Task Webhook] Error en segundo plano: {e}")

@router.post("")
async def recibir_mensaje(request: Request, background_tasks: BackgroundTasks):
    """
    Punto de entrada principal asíncrono para recibir mensajes (Meta Cloud API / Twilio).
    Responde en < 2 segundos (HTTP 200 OK) y delega la ejecución pesada a BackgroundTasks.
    """
    t_inicio = time.time()
    remitente = "desconocido"
    tipo_mensaje = "text"
    texto_cliente = ""
    audio_id = ""
    placa = "WAPP-01"
    marca_modelo = "Vehiculo Generico"

    content_type = request.headers.get("content-type", "").lower()

    try:
        # 1. Soporte para formulario Twilio (application/x-www-form-urlencoded)
        if "application/x-www-form-urlencoded" in content_type:
            try:
                form_data = await request.form()
                remitente = form_data.get("From", "whatsapp:+51000000000")
                texto_cliente = form_data.get("Body", "")
                media_url = form_data.get("MediaUrl0", "")
            except Exception as fe:
                logger.warning(f"Error al analizar form data con python-multipart, ejecutando fallback urllib.parse: {fe}")
                body_bytes = await request.body()
                body_str = body_bytes.decode('utf-8', errors='ignore')
                from urllib.parse import parse_qs
                parsed = parse_qs(body_str)
                remitente = parsed.get("From", ["whatsapp:+51000000000"])[0]
                texto_cliente = parsed.get("Body", [""])[0]
                media_url = parsed.get("MediaUrl0", [""])[0]

            if media_url:
                tipo_mensaje = "audio"
                audio_id = media_url
            logger.info(f"[Webhook Twilio] Mensaje recibido de {remitente}: {texto_cliente}")
        
        # 2. Soporte para JSON Payload (Meta Cloud API o DTO Custom)
        else:
            payload = await request.json()
            
            # Formato Meta Cloud API (Graph API)
            if "entry" in payload:
                entry = payload.get("entry", [])[0]
                changes = entry.get("changes", [])[0]
                value = changes.get("value", {})
                messages = value.get("messages", [])
                
                if messages:
                    msg = messages[0]
                    remitente = msg.get("from", "desconocido")
                    tipo_mensaje = msg.get("type", "text")
                    if tipo_mensaje == "text":
                        texto_cliente = msg.get("text", {}).get("body", "")
                    elif tipo_mensaje == "audio":
                        audio_id = msg.get("audio", {}).get("id", "")
                    logger.info(f"[Webhook Meta API] Mensaje de {remitente} (Tipo: {tipo_mensaje})")
            
            # Formato DTO directo (Twilio/Custom WhatsApp Payload DTO)
            elif "from_number" in payload or "body_text" in payload or "sintoma" in payload:
                remitente = payload.get("from_number") or payload.get("remitente", "whatsapp:+51000000000")
                texto_cliente = payload.get("body_text") or payload.get("sintoma", "")
                tipo_mensaje = payload.get("message_type", "text")
                audio_id = payload.get("media_url", "")
                placa = payload.get("placa", "WAPP-01")
                marca_modelo = payload.get("marca_modelo", "Vehiculo Generico")
                logger.info(f"[Webhook JSON Directo] Mensaje de {remitente}: {texto_cliente}")

        # Delegar ejecución en segundo plano (ML + RAG + Gemini + Tracker + Meta POST)
        background_tasks.add_task(
            _procesar_y_responder_whatsapp,
            remitente=remitente,
            tipo_mensaje=tipo_mensaje,
            texto_cliente=texto_cliente,
            audio_id=audio_id,
            placa=placa,
            marca_modelo=marca_modelo,
            session_id=remitente
        )

    except Exception as e:
        logger.error(f"Error al procesar payload del Webhook WhatsApp: {e}")

    t_fin = time.time()
    elapsed_ms = (t_fin - t_inicio) * 1000

    # Responder de forma ultra-rápida en < 2 segundos (generalmente < 50ms)
    return JSONResponse(
        status_code=200,
        content={
            "status": "procesado",
            "mensaje": "Mensaje recibido en cola de procesamiento asíncrono",
            "tiempo_respuesta_ms": round(elapsed_ms, 2)
        }
    )

def enviar_mensaje_whatsapp(numero_destino: str, texto: str):
    """Realiza la llamada HTTP POST a la Graph API de Meta para enviar el mensaje."""
    token_activo = settings.TOKEN_WHATSAPP
    telefono_id_activo = settings.TELEFONO_ID
    
    if not token_activo or not telefono_id_activo:
        logger.warning("No se enviará mensaje vía HTTP Meta API (Falta TOKEN_WHATSAPP o TELEFONO_ID).")
        return

    url = f"https://graph.facebook.com/v18.0/{telefono_id_activo}/messages"
    headers = {
        "Authorization": f"Bearer {token_activo}",
        "Content-Type": "application/json"
    }
    data = {
        "messaging_product": "whatsapp",
        "to": numero_destino,
        "type": "text",
        "text": {
            "body": texto
        }
    }
    try:
        res = requests.post(url, headers=headers, json=data, timeout=5)
        logger.info(f"Respuesta enviada a {numero_destino}. Meta Status Code: {res.status_code}")
        if res.status_code != 200:
            logger.error(f"Detalle del error de Meta API: {res.text}")
    except Exception as e:
        logger.error(f"Falló el envío del mensaje vía HTTP a Meta API: {e}")
