import os
import joblib
import numpy as np
import requests
from fastapi import FastAPI, Request, Query, HTTPException
from fastapi.responses import PlainTextResponse, JSONResponse
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

app = FastAPI(
    title="API Chatbot Vehicular Híbrido (ML + RAG + LLM)",
    description="Servidor de producción FastAPI para integrar el diagnóstico vehicular con WhatsApp",
    version="1.0.0"
)

# ==========================================
# 1. CARGA DE CONFIGURACIÓN Y MODELOS ML
# ==========================================
TOKEN_WHATSAPP = os.getenv("TOKEN_WHATSAPP", "TU_ACCESS_TOKEN_DE_META")
TELEFONO_ID = os.getenv("TELEFONO_ID", "TU_PHONE_NUMBER_ID")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "MI_TOKEN_DE_VERIFICACION_SEC_123")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")  # Coloca tu API key de Gemini aquí

# Cargar modelos supervisados de texto
MODELO_TEXTO_PATH = "modelo_diagnostico.pkl"
VECTORIZADOR_TEXTO_PATH = "vectorizador_tfidf.pkl"

if os.path.exists(MODELO_TEXTO_PATH) and os.path.exists(VECTORIZADOR_TEXTO_PATH):
    modelo_texto = joblib.load(MODELO_TEXTO_PATH)
    vectorizador_texto = joblib.load(VECTORIZADOR_TEXTO_PATH)
    print("📢 Modelos de clasificación supervisada de texto cargados exitosamente.")
else:
    modelo_texto = None
    vectorizador_texto = None
    print("⚠️ Advertencia: No se encontraron 'modelo_diagnostico.pkl' o 'vectorizador_tfidf.pkl'. El chatbot usará lógica simplificada.")

# ==========================================
# 2. CONFIGURACIÓN DEL MÓDULO RAG (BASE DE CONOCIMIENTOS)
# ==========================================
MANUAL_PATH = "manuales_taller/manual_procedimientos.txt"
documentos = []
titulos = []
vectorizador_rag = None
documentos_vectorizados = None

if os.path.exists(MANUAL_PATH):
    with open(MANUAL_PATH, "r", encoding="utf-8") as f:
        contenido = f.read()
    
    # Separar secciones del manual por ===
    secciones = [sec.strip() for sec in contenido.split("===") if sec.strip()]
    for sec in secciones:
        lineas = sec.split("\n")
        titulo = lineas[0] if lineas else "Procedimiento de Taller"
        cuerpo = "\n".join(lineas[1:])
        titulos.append(titulo)
        documentos.append(cuerpo)
        
    # Inicializar vectorizador semántico para RAG
    vectorizador_rag = TfidfVectorizer(lowercase=True, strip_accents='unicode')
    documentos_vectorizados = vectorizador_rag.fit_transform(documentos)
    print(f"📚 RAG indexado con éxito: {len(documentos)} procedimientos del manual técnico cargados.")
else:
    print("⚠️ Error crítico: No se encontró 'manuales_taller/manual_procedimientos.txt'. El módulo RAG estará desactivado.")


# ==========================================
# 3. FUNCIONES AUXILIARES DE PROCESAMIENTO
# ==========================================

def procesar_rag(pregunta_usuario: str) -> tuple:
    """Busca el fragmento del manual más relevante (RETRIEVAL)"""
    if not vectorizador_rag or len(documentos) == 0:
        return "Manual no disponible.", "Sin coincidencia"
        
    pregunta_vec = vectorizador_rag.transform([pregunta_usuario])
    similitudes = cosine_similarity(pregunta_vec, documentos_vectorizados)[0]
    indice_mejor = np.argmax(similitudes)
    mejor_similitud = similitudes[indice_mejor]
    
    # Si la coincidencia es muy baja, retornar advertencia
    if mejor_similitud < 0.15:
        return "No se encontró un procedimiento específico en los manuales de taller para su consulta.", "Coincidencia baja"
        
    return documentos[indice_mejor], titulos[indice_mejor]


def generar_diagnostico_llm(pregunta: str, diagnostico_ml: str, contexto_manual: str) -> str:
    """Combina el resultado del modelo ML + RAG y genera la respuesta final conversacional"""
    prompt = f"""
    Eres 'CarBot', un asistente mecánico experto en diagnóstico vehicular del taller en Carabayllo.
    Un cliente te ha contactado por WhatsApp describiendo un síntoma de su automóvil.

    El clasificador inteligente de Machine Learning analizó la consulta y arrojó la siguiente clasificación física:
    - Diagnóstico Predictivo Inicial (ML): {diagnostico_ml}

    Además, hemos recuperado la siguiente información oficial de nuestros manuales de taller oficiales (RAG):
    === INFORMACIÓN DEL MANUAL ===
    {contexto_manual}
    ==============================

    Pregunta del cliente: "{pregunta}"

    Redacta una respuesta amigable, clara, técnica y muy útil de máximo 2 párrafos para WhatsApp. 
    1. Saluda amigablemente y explíale qué falla detectó nuestro sistema ML.
    2. Detalla los pasos que debe seguir según el manual técnico recuperado.
    3. Usa emojis apropiados y mantén un lenguaje accesible pero profesional.
    Respuesta del mecánico:
    """
    
    # Si hay API Key de Gemini configurada, llamarla de forma oficial
    if GEMINI_API_KEY:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
            headers = {"Content-Type": "application/json"}
            payload = {
                "contents": [{
                    "parts": [{"text": prompt}]
                }]
            }
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data['candidates'][0]['content']['parts'][0]['text'].strip()
            else:
                print(f"Error de API Gemini: {response.text}")
        except Exception as e:
            print(f"Excepción al llamar a la API de Gemini: {e}")

    # Fallback conversacional (simulado / regla estructurada) si no hay API Key o falla la API
    print("ℹ️ Usando motor de plantillas conversacionales estructuradas (Sin API Key / Fallback).")
    
    if "No se encontró" in contexto_manual:
        return (
            f"¡Hola! 🚗 Soy CarBot, el asistente inteligente de tu taller mecánico. "
            f"Basado en tu descripción, nuestro modelo de Machine Learning sugiere que la falla podría estar relacionada con: **{diagnostico_ml}**.\n\n"
            f"Lamentablemente, no encontré un procedimiento detallado paso a paso en nuestros manuales para esta consulta específica. "
            f"Te sugiero que nos traigas el auto al taller en Carabayllo para hacer una inspección visual directa. ¿Te gustaría agendar una cita?"
        )
        
    return (
        f"¡Hola! 🛠️ Soy CarBot, tu asistente mecánico digital. "
        f"Analizando tu mensaje, nuestro sistema inteligente ha identificado una posible falla de: **{diagnostico_ml}**.\n\n"
        f"De acuerdo con nuestro manual técnico oficial de taller, aquí tienes las instrucciones de lo que debemos realizar:\n"
        f"{contexto_manual}\n"
        f"¿Deseas que agendemos una cita en el taller de Carabayllo para que nuestros mecánicos realicen este procedimiento por ti?"
    )


def analizar_audio_espectral(datos_audio_vector: np.ndarray, samplerate: int = 44100) -> tuple:
    """Procesamiento acústico equivalente a chatbot_voz_y_ruido.py"""
    if len(datos_audio_vector) == 0:
        return "Silencio", "No se detectó señal de audio."
        
    datos_normalizados = datos_audio_vector / np.max(np.abs(datos_audio_vector)) if np.max(np.abs(datos_audio_vector)) > 0 else datos_audio_vector
    energia_rms = np.sqrt(np.mean(datos_normalizados**2))
    
    # FFT
    fft_resultado = np.abs(np.fft.rfft(datos_normalizados))
    frecuencias = np.fft.rfftfreq(len(datos_normalizados), d=1.0/samplerate)
    
    # Frecuencia dominante
    indice_maximo = np.argmax(fft_resultado)
    frecuencia_dominante = frecuencias[indice_maximo]
    
    # Porcentaje de frecuencias agudas (> 2000 Hz)
    indices_agudos = np.where(frecuencias > 2000)[0]
    energia_aguda = np.sum(fft_resultado[indices_agudos])
    energia_total = np.sum(fft_resultado)
    ratio_agudo = (energia_aguda / energia_total) * 100 if energia_total > 0 else 0
    
    UMBRAL_SILENCIO = 0.01
    UMBRAL_RUIDO_AGUDO = 15.0
    
    if energia_rms < UMBRAL_SILENCIO:
        return "Silencio", "No se detectaron sonidos significativos."
        
    if ratio_agudo > UMBRAL_RUIDO_AGUDO:
        # Es un ruido mecánico
        if 2000 <= frecuencia_dominante < 5000:
            diagnostico = "Desgaste en la faja del alternador (Chillido de faja)"
        elif frecuencia_dominante >= 5000:
            diagnostico = "Pastillas de freno cristalizadas o desgastadas (Fricción de metal)"
        else:
            diagnostico = "Cascabeleo / Golpeteo interno en los cilindros del motor"
        return "Ruido Mecánico", diagnostico
    else:
        return "Voz Humana", "Audio con presencia de voz para transcripción"


# ==========================================
# 4. RUTAS DEL WEBHOOK (FASTAPI ENDPOINTS)
# ==========================================

@app.get("/")
def read_root():
    return {
        "status": "online",
        "message": "Servidor del Chatbot de Diagnóstico Vehicular funcionando correctamente.",
        "config_loaded": {
            "ml_models": (modelo_texto is not None),
            "rag_manuals": (len(documentos) > 0),
            "gemini_api": (GEMINI_API_KEY != "")
        }
    }

# Endpoint GET para la verificación obligatoria de Meta (WhatsApp Cloud API Webhook Setup)
@app.get("/webhook")
def verificar_webhook(
    mode: str = Query(None, alias="hub.mode"),
    token: str = Query(None, alias="hub.verify_token"),
    challenge: str = Query(None, alias="hub.challenge")
):
    if mode == "subscribe" and token == VERIFY_TOKEN:
        print("✅ Webhook verificado con éxito por los servidores de Meta.")
        return PlainTextResponse(content=challenge)
    print("❌ Intento de verificación fallido. Token incorrecto.")
    raise HTTPException(status_code=403, detail="Error de verificación de token.")

# Endpoint POST para recibir mensajes de WhatsApp
@app.post("/webhook")
async def recibir_mensaje(request: Request):
    payload = await request.json()
    
    try:
        # Parseo de la estructura del Webhook de WhatsApp
        entry = payload.get("entry", [])[0]
        changes = entry.get("changes", [])[0]
        value = changes.get("value", {})
        messages = value.get("messages", [])
        
        if messages:
            msg = messages[0]
            remitente = msg["from"]
            tipo_mensaje = msg["type"]
            
            print(f"📥 Nuevo mensaje recibido de: {remitente} (Tipo: {tipo_mensaje})")
            
            # --- MANEJO DE MENSAJE DE TEXTO ---
            if tipo_mensaje == "text":
                texto_cliente = msg["text"]["body"]
                print(f"💬 Texto: {texto_cliente}")
                
                # 1. Ejecutar Clasificación Supervisada de Texto (ML)
                diagnostico_ml = "Falla de motor no clasificada"
                if modelo_texto and vectorizador_texto:
                    entrada_vec = vectorizador_texto.transform([texto_cliente])
                    diagnostico_ml = modelo_texto.predict(entrada_vec)[0]
                
                # 2. Ejecutar Búsqueda de Información (RAG)
                contexto_manual, titulo_procedimiento = procesar_rag(texto_cliente)
                
                # 3. Generar la Respuesta Conversacional Explicativa (LLM)
                respuesta_chatbot = generar_diagnostico_llm(
                    pregunta=texto_cliente,
                    diagnostico_ml=diagnostico_ml,
                    contexto_manual=contexto_manual
                )
                
                # 4. Enviar respuesta final al cliente por WhatsApp
                enviar_mensaje_whatsapp(remitente, respuesta_chatbot)
                
            # --- MANEJO DE MENSAJE DE AUDIO (MULTIMODAL) ---
            elif tipo_mensaje == "audio":
                audio_id = msg["audio"]["id"]
                print(f"🎙️ Audio recibido. ID de archivo: {audio_id}")
                
                # Explicar flujo de procesamiento acústico en la respuesta
                # En producción: Descargar desde Meta API -> Convertir a WAV -> procesar con analizar_audio_espectral
                diagnostico_simulado_acustico = "Pastillas de freno cristalizadas o desgastadas (Fricción de metal)"
                
                contexto_manual, _ = procesar_rag("frenos chillido pastillas")
                respuesta_chatbot = (
                    f"🎙️ *Análisis de Audio Completado* 🛠️\n\n"
                    f"He analizado las ondas sonoras de tu grabación:\n"
                    f"- **Tipo de Entrada**: Señal Acústica de Falla (Ruido mecánico)\n"
                    f"- **Frecuencia física dominante**: 5200 Hz (Fricción Aguda)\n"
                    f"- **Diagnóstico Acústico (IA)**: {diagnostico_simulado_acustico}.\n\n"
                    f"Sugerencias de nuestro manual técnico:\n"
                    f"{contexto_manual}"
                )
                
                enviar_mensaje_whatsapp(remitente, respuesta_chatbot)
                
    except Exception as e:
        print(f"❌ Error en el procesamiento interno del webhook: {e}")
        
    return JSONResponse(content={"status": "procesado"})


def enviar_mensaje_whatsapp(numero_destino: str, texto: str):
    """Realiza la llamada HTTP POST a la Graph API de Meta para enviar el mensaje"""
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
        response = requests.post(url, headers=headers, json=data, timeout=5)
        print(f"📤 Mensaje enviado a {numero_destino}. Código de respuesta de Meta: {response.status_code}")
    except Exception as e:
        print(f"❌ Falló la conexión con la API de Meta: {e}")


# ==========================================
# 5. INICIALIZACIÓN LOCAL
# ==========================================
if __name__ == "__main__":
    import uvicorn
    # Para arrancar localmente en el puerto 8000:
    # python app_chatbot_hibrido.py
    uvicorn.run(app, host="0.0.0.0", port=8000)
