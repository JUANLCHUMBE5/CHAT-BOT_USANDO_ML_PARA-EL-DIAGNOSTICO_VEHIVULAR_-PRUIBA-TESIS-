import time
from urllib.parse import parse_qs
import requests
from fastapi import APIRouter, Request, Query, HTTPException, BackgroundTasks, Header
from fastapi.responses import PlainTextResponse, JSONResponse
from fastapi.concurrency import run_in_threadpool
from src.core.gestor_diagnostico import GestorDiagnostico, ResultadoDiagnostico as DTOInternal
from src.core.security import verificar_firma_meta, verificar_firma_twilio, anonimizar_identificador
from src.core.logger import logger
from src.config import settings

router = APIRouter()

def obtener_gestor_diagnostico(request: Request) -> GestorDiagnostico:
    if hasattr(request.app.state, "gestor_diagnostico"):
        return request.app.state.gestor_diagnostico
    return GestorDiagnostico()

async def _procesar_y_responder_whatsapp(
    gestor: GestorDiagnostico,
    remitente: str, 
    tipo_mensaje: str, 
    texto_cliente: str = "", 
    audio_id: str = "",
    placa: str = "WAPP-01",
    marca_modelo: str = "Vehiculo Generico",
    session_id: str = None
):
    """Procesa en segundo plano la consulta de forma thread-safe y responde vía WhatsApp."""
    start_t = time.time()
    try:
        id_sesion = session_id or remitente
        if tipo_mensaje == "text":
            resultado_dto: DTOInternal = await run_in_threadpool(
                gestor.procesar_consulta_texto,
                texto_cliente, 
                placa=placa, 
                marca_modelo=marca_modelo, 
                session_id=id_sesion
            )
            respuesta = resultado_dto.respuesta_texto
        elif tipo_mensaje == "audio":
            respuesta = await run_in_threadpool(gestor.procesar_consulta_audio, audio_id)
        else:
            respuesta = "Lo siento, actualmente solo puedo procesar mensajes de texto y notas de audio."

        # Enviar mensaje de respuesta a la Graph API de Meta si hay número válido
        if remitente and not remitente.startswith("test") and settings.TOKEN_WHATSAPP:
            await run_in_threadpool(enviar_mensaje_whatsapp, remitente, respuesta)

        elapsed = (time.time() - start_t) * 1000
        rem_anon = anonimizar_identificador(remitente)
        logger.info(f"[Background Task Webhook] Procesado con éxito en {elapsed:.2f} ms para usuario {rem_anon}")
    except Exception as e:
        logger.error(f"[Background Task Webhook] Error en segundo plano: {e}")

# ==========================================
# ENDPOINTS META WHATSAPP CLOUD API
# ==========================================

@router.get("/meta", summary="Verificación Webhook Meta Cloud API")
@router.get("", summary="Verificación Webhook Meta (Compatibilidad)")
def verificar_webhook_meta(
    mode: str = Query(None, alias="hub.mode"),
    token: str = Query(None, alias="hub.verify_token"),
    challenge: str = Query(None, alias="hub.challenge")
):
    """Verificación obligatoria del Webhook requerida por Meta Cloud API."""
    expected_token = getattr(settings, "META_VERIFY_TOKEN", getattr(settings, "VERIFY_TOKEN", "carbot_verify_token_ucv_2026"))
    verify_token_alt = getattr(settings, "VERIFY_TOKEN", "")
    if mode == "subscribe" and (token == expected_token or (verify_token_alt and token == verify_token_alt)):
        logger.info("Webhook de WhatsApp verificado con éxito por Meta.")
        return PlainTextResponse(content=challenge or "")
    logger.warning("Intento de verificación de Webhook fallido por token incorrecto.")
    raise HTTPException(status_code=403, detail="Token de verificación inválido (Verify token incorrecto).")

@router.post("/meta", summary="Recepción de Mensajes Meta Cloud API")
async def recibir_mensaje_meta(
    request: Request,
    background_tasks: BackgroundTasks,
    x_hub_signature_256: str = Header(None, alias="X-Hub-Signature-256")
):
    """
    Webhook dedicado para Meta Cloud API (WhatsApp).
    Requiere obligatoriamente firma criptográfica X-Hub-Signature-256 válida. Falla cerrado si el secret falta o no coincide.
    """
    t_inicio = time.time()
    raw_body = await request.body()

    if not x_hub_signature_256 or not verificar_firma_meta(raw_body, x_hub_signature_256):
        logger.warning("[Webhook Meta] Firma criptográfica X-Hub-Signature-256 inválida o ausente.")
        raise HTTPException(status_code=401, detail="Firma de webhook inválida (Unauthorized Meta Payload).")

    try:
        payload = await request.json()
        remitente = "desconocido"
        tipo_mensaje = "text"
        texto_cliente = ""
        audio_id = ""

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
        else:
            raise HTTPException(status_code=400, detail="Formato de payload Meta inválido.")

        rem_anon = anonimizar_identificador(remitente)
        logger.info(f"[Webhook Meta API] Mensaje válido de usuario {rem_anon} (Tipo: {tipo_mensaje})")

        gestor = obtener_gestor_diagnostico(request)
        background_tasks.add_task(
            _procesar_y_responder_whatsapp,
            gestor=gestor,
            remitente=remitente,
            tipo_mensaje=tipo_mensaje,
            texto_cliente=texto_cliente,
            audio_id=audio_id,
            placa="WAPP-01",
            marca_modelo="Vehiculo Generico",
            session_id=remitente
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Webhook Meta] Error al procesar payload: {e}")
        raise HTTPException(status_code=400, detail="Formato de payload Meta inválido.")

    elapsed_ms = (time.time() - t_inicio) * 1000
    return JSONResponse(
        status_code=200,
        content={
            "status": "procesado",
            "proveedor": "Meta Cloud API",
            "tiempo_respuesta_ms": round(elapsed_ms, 2)
        }
    )

# ==========================================
# ENDPOINT TWILIO WHATSAPP
# ==========================================

@router.post("/twilio", summary="Recepción de Mensajes Twilio Form")
async def recibir_mensaje_twilio(
    request: Request,
    background_tasks: BackgroundTasks,
    x_twilio_signature: str = Header(None, alias="X-Twilio-Signature")
):
    """
    Webhook dedicado para Twilio (Form-urlencoded).
    Valida la firma criptográfica X-Twilio-Signature. Falla cerrado si el token o la firma no coinciden.
    """
    t_inicio = time.time()
    raw_body = await request.body()
    body_str = raw_body.decode('utf-8', errors='ignore')
    parsed_qs = parse_qs(body_str)

    # Convertir dict de listas de parse_qs a valores simples
    params_dict = {k: v[0] for k, v in parsed_qs.items() if v}

    url_solicitud = str(request.url)
    if not x_twilio_signature or not verificar_firma_twilio(url_solicitud, params_dict, x_twilio_signature):
        logger.warning("[Webhook Twilio] Firma criptográfica X-Twilio-Signature inválida o ausente.")
        raise HTTPException(status_code=401, detail="Firma de webhook inválida (Unauthorized Twilio Payload).")

    remitente = params_dict.get("From", "whatsapp:+51000000000")
    texto_cliente = params_dict.get("Body", "")
    media_url = params_dict.get("MediaUrl0", "")
    tipo_mensaje = "audio" if media_url else "text"
    audio_id = media_url if media_url else ""

    rem_anon = anonimizar_identificador(remitente)
    logger.info(f"[Webhook Twilio] Mensaje verificado recibido de {rem_anon}")

    gestor = obtener_gestor_diagnostico(request)
    background_tasks.add_task(
        _procesar_y_responder_whatsapp,
        gestor=gestor,
        remitente=remitente,
        tipo_mensaje=tipo_mensaje,
        texto_cliente=texto_cliente,
        audio_id=audio_id,
        placa="WAPP-01",
        marca_modelo="Vehiculo Generico",
        session_id=remitente
    )

    elapsed_ms = (time.time() - t_inicio) * 1000
    return JSONResponse(
        status_code=200,
        content={
            "status": "procesado",
            "proveedor": "Twilio",
            "tiempo_respuesta_ms": round(elapsed_ms, 2)
        }
    )

# ==========================================
# ENDPOINT RAÍZ COMPATIBILIDAD
# ==========================================

@router.post("", summary="Recepción Webhook Raíz (Enrutamiento Criptográfico)")
async def recibir_mensaje(
    request: Request,
    background_tasks: BackgroundTasks,
    x_hub_signature_256: str = Header(None, alias="X-Hub-Signature-256"),
    x_twilio_signature: str = Header(None, alias="X-Twilio-Signature")
):
    """
    Punto de entrada general con enrutamiento automático hacia /meta o /twilio según firmas e inspección del payload.
    Exige firma criptográfica válida de alguno de los proveedores.
    """
    content_type = request.headers.get("content-type", "").lower()

    if "application/x-www-form-urlencoded" in content_type or x_twilio_signature:
        return await recibir_mensaje_twilio(request, background_tasks, x_twilio_signature)

    return await recibir_mensaje_meta(request, background_tasks, x_hub_signature_256)

def enviar_mensaje_whatsapp(numero_destino: str, texto: str):
    """Realiza la llamada HTTP POST a la Graph API de Meta para enviar la respuesta."""
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
        rem_anon = anonimizar_identificador(numero_destino)
        logger.info(f"Respuesta enviada a usuario {rem_anon}. Meta Status Code: {res.status_code}")
    except Exception as e:
        logger.error(f"Falló el envío del mensaje vía HTTP a Meta API: {e}")
