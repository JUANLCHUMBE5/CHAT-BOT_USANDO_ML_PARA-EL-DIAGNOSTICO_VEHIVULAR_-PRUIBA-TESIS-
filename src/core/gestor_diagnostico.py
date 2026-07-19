import os
import requests
from src.infrastructure.modelo_ml import ModeloML
from src.infrastructure.motor_rag import MotorRAG
from src.core.audio_processor import AudioProcessor

class GestorDiagnostico:
    """Clase orquestadora encargada de coordinar el flujo de diagnóstico (ML + RAG + LLM)."""
    
    def __init__(self, gemini_api_key: str = ""):
        self.api_key = gemini_api_key or os.getenv("GEMINI_API_KEY", "")
        self.modelo_ml = ModeloML()
        self.motor_rag = MotorRAG()
        self.procesador_audio = AudioProcessor()

    def procesar_consulta_texto(self, texto_usuario: str) -> str:
        """Flujo completo para consultas de texto (ML + RAG + LLM)"""
        # 1. Clasificar con Machine Learning
        diagnostico_predictivo = self.modelo_ml.predecir_falla(texto_usuario)
        
        # 2. Recuperar del manual (RAG)
        contexto_manual, titulo_manual = self.motor_rag.recuperar_contexto(texto_usuario)
        
        # 3. Generar la respuesta final usando LLM
        respuesta_explicativa = self.generar_respuesta_conversacional(
            pregunta=texto_usuario,
            diagnostico_ml=diagnostico_predictivo,
            contexto_manual=contexto_manual
        )
        
        return respuesta_explicativa

    def procesar_consulta_audio(self, audio_id: str, datos_audio_vector = None) -> str:
        """Flujo completo para audios (Inactivo por cumplimiento de protocolo ético)"""
        return (
            "🎙️ *Función de Audio Inactiva por Protocolo de Ética*\n\n"
            "Estimado usuario, para cumplir estrictamente con los protocolos de consentimiento, "
            "confidencialidad y protección de datos aprobados por el Comité de Ética de la universidad, "
            "el procesamiento directo de mensajes de voz y audio está inactivo en la versión oficial del sistema.\n\n"
            "Por favor, ✍️ *escriba los síntomas de su vehículo por mensaje de texto* para poder brindarle un diagnóstico automático asistido por Machine Learning y RAG."
        )

    def generar_respuesta_conversacional(self, pregunta: str, diagnostico_ml: str, contexto_manual: str) -> str:
        """Envía el prompt aumentado con RAG y clasificación ML a la API de Gemini (o fallback local)"""
        prompt_sistema = f"""
        Eres 'CarBot', un asistente técnico de soporte inteligente para el mecánico del taller en Carabayllo.
        
        Información del sistema de IA:
        - Nuestro modelo de Machine Learning predijo que la falla se asocia con: {diagnostico_ml}
        - Información del manual técnico de taller recuperada (RAG):
        {contexto_manual}
        
        Consulta técnica del mecánico: "{pregunta}"
        
        Redacta una respuesta concisa, técnica y muy útil para el mecánico a través de WhatsApp, de máximo 2 párrafos. Usa emojis.
        Confírmale el diagnóstico sugerido por el modelo ML y detalla los pasos de reparación específicos del manual de taller.
        Respuesta:
        """
        
        if self.api_key:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.api_key}"
                headers = {"Content-Type": "application/json"}
                payload = {
                    "contents": [{"parts": [{"text": prompt_sistema}]}]
                }
                response = requests.post(url, json=payload, headers=headers, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    return data['candidates'][0]['content']['parts'][0]['text'].strip()
            except Exception as e:
                print(f"❌ Error al consultar la API de Gemini: {e}")
                
        # Fallback local conversacional si no hay clave API
        if "No se encontró" in contexto_manual:
            return (
                f"🛠️ **CarBot - Asistente de Taller**\n\n"
                f"El modelo de Machine Learning sugiere que la falla se asocia con: **{diagnostico_ml}**.\n\n"
                f"⚠️ *Nota:* No se encontró un procedimiento específico en el manual de taller para esta consulta. "
                f"Te sugiero revisar componentes asociados o realizar pruebas visuales directas en el vehículo."
            )
            
        return (
            f"🛠️ **CarBot - Asistente de Taller**\n\n"
            f"El modelo de Machine Learning sugiere que la falla se asocia con: **{diagnostico_ml}**.\n\n"
            f"📖 *Procedimiento según el manual de taller*:\n"
            f"{contexto_manual}\n\n"
            f"¿Necesitas que te ayude a buscar otra falla o procedimiento técnico en el manual?"
        )
