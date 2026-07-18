import os
import requests
from fastapi import APIRouter, Request, Query, HTTPException
from fastapi.responses import PlainTextResponse, JSONResponse
from src.core.gestor_diagnostico import GestorDiagnostico

# Crear enrutador FastAPI para Webhook
router = APIRouter()

# Configuración desde variables de entorno
TOKEN_WHATSAPP = os.getenv("TOKEN_WHATSAPP", "TU_ACCESS_TOKEN_DE_META")
TELEFONO_ID = os.getenv("TELEFONO_ID", "TU_PHONE_NUMBER_ID")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "MI_TOKEN_DE_VERIFICACION_SEC_123")

# Instanciar el orquestador core de diagnóstico
gestor = GestorDiagnostico()

@router.get("")
def verificar_webhook(
    mode: str = Query(None, alias="hub.mode"),
    token: str = Query(None, alias="hub.verify_token"),
    challenge: str = Query(None, alias="hub.challenge")
):
    """Verificación obligatoria del Webhook requerida por los servidores de Meta."""
    if mode == "subscribe" and token == VERIFY_TOKEN:
        print("✅ Webhook de WhatsApp verificado con éxito por Meta.")
        return PlainTextResponse(content=challenge)
    raise HTTPException(status_code=403, detail="Verify token incorrecto.")

@router.post("")
async def recibir_mensaje(request: Request):
    """Punto de entrada principal para recibir mensajes y audios desde WhatsApp."""
    payload = await request.json()
    
    try:
        entry = payload.get("entry", [])[0]
        changes = entry.get("changes", [])[0]
        value = changes.get("value", {})
        messages = value.get("messages", [])
        
        if messages:
            msg = messages[0]
            remitente = msg["from"]
            tipo_mensaje = msg["type"]
            
            print(f"📥 [Webhook API v1] Nuevo mensaje de {remitente} (Tipo: {tipo_mensaje})")
            
            # 1. Procesar según tipo de mensaje
            if tipo_mensaje == "text":
                texto_cliente = msg["text"]["body"]
                # Invocar capa de aplicación (Core)
                respuesta = gestor.procesar_consulta_texto(texto_cliente)
                
            elif tipo_mensaje == "audio":
                audio_id = msg["audio"]["id"]
                # En producción se descargaría y convertiría el audio a vector numpy
                # Aquí se pasa a la capa de aplicación (Core) para diagnóstico
                respuesta = gestor.procesar_consulta_audio(audio_id)
                
            else:
                respuesta = "Lo siento, actualmente solo puedo procesar mensajes de texto y notas de audio."

            # 2. Enviar respuesta final a WhatsApp
            enviar_mensaje_whatsapp(remitente, respuesta)
            
    except Exception as e:
        print(f"❌ Error en el procesamiento del Webhook de WhatsApp: {e}")
        
    return JSONResponse(content={"status": "procesado"})

def enviar_mensaje_whatsapp(numero_destino: str, texto: str):
    """Realiza la llamada HTTP POST a la Graph API de Meta para enviar el mensaje."""
    url = f"https://graph.facebook.com/v18.0/{TELEFONO_ID}/messages"
    headers = {
        "Authorization": f"Bearer {TOKEN_WHATSAPP}",
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
        print(f"📤 Respuesta enviada a {numero_destino}. Meta Status Code: {res.status_code}")
    except Exception as e:
        print(f"❌ Falló el envío del mensaje vía HTTP a Meta API: {e}")
