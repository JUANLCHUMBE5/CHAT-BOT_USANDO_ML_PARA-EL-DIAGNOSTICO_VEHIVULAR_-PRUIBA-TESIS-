from typing import Optional
import os
import threading
import requests
import numpy as np
import pandas as pd
from src.infrastructure.modelo_ml import ModeloML
from src.infrastructure.motor_rag import MotorRAG
from src.core.audio_processor import AudioProcessor
from src.core.session_manager import SessionManager
from src.core.traductor_jerga import normalizar_jerga_peruana
from src.core.logger import logger
from src.config import settings

_tracker_lock = threading.Lock()

class GestorDiagnostico:
    """Clase orquestadora encargada de coordinar el flujo de diagnóstico (ML + RAG + LLM)."""
    
    def __init__(self, gemini_api_key: str = ""):
        self.api_key = gemini_api_key or settings.GEMINI_API_KEY
        self.modelo_ml = ModeloML()
        self.motor_rag = MotorRAG()
        self.procesador_audio = AudioProcessor()
        self.session_manager = SessionManager()
        self.ultimo_diagnostico_ml: str = "Diagnóstico Conversacional"
        self.ultima_confianza: float = 1.0
        self.ultimo_contexto_manual: str = ""
        self.ultimo_titulo_manual: str = ""

    def _es_saludo_o_contacto_inicial(self, texto: str) -> tuple:
        """Detecta si el mensaje es un saludo o contacto inicial sin detalles mecánicos."""
        texto_limpio = texto.strip().lower()
        
        saludos = [
            "hola", "holaa", "holaaa", "buenas", "buenos dias", "buenas tardes", "buenas noches",
            "hola tengo un problema", "hola tengo problemas",
            "tengo una falla", "hola buenas", "saludos", "hola que tal", "ayuda", "consulta"
        ]
        
        palabras_mecanicas = [
            "freno", "frenos", "motor", "bujia", "bujias", "bateria", "arranque", "arrancar",
            "acelerar", "cuesta", "humo", "rueda", "timon", "volante", "caja", "cambio", "pedal",
            "chillido", "cascabeleo", "esponjoso", "apaga", "tiembla", "vibracion", "sonido", "ruido", "scanner", "dtc", "p0"
        ]
        
        tiene_palabra_mecanica = any(pm in texto_limpio for pm in palabras_mecanicas)
        
        if texto_limpio in saludos or (any(s in texto_limpio for s in ["hola", "buenas"]) and not tiene_palabra_mecanica):
            return True, "👋 ¡Hola! Bienvenido a CarBot. Por favor, cuéntame: **¿Qué problema o síntoma presenta tu vehículo hoy?**"
        return False, ""

    def _es_consulta_ambigua(self, texto: str) -> tuple:
        """Determina si la consulta del usuario es incompleta o ambigua (Requerimiento R1)."""
        texto_limpio = texto.strip().lower()
        words = texto_limpio.split()
        
        frases_ambiguas = [
            "el carro falla", "mi auto falla", "mi carro falla", "tengo un problema", "tengo problemas",
            "tengo una falla", "ayuda", "ruido", "freno", "motor", "falla el carro"
        ]
        
        palabras_mecanicas = [
            "freno", "frenos", "motor", "bujia", "bujias", "bateria", "arranque", "arrancar",
            "acelerar", "cuesta", "humo", "rueda", "timon", "volante", "caja", "cambio", "pedal",
            "chillido", "cascabeleo", "esponjoso", "apaga", "tiembla", "vibracion", "sonido", "ruido", "scanner", "dtc", "p0"
        ]
        
        tiene_palabra_mecanica = any(pm in texto_limpio for pm in palabras_mecanicas)
        
        if len(words) < 3 or texto_limpio in frases_ambiguas or not tiene_palabra_mecanica:
            return True, "⚠️ Por favor, especifique el síntoma con más detalle (ej. si ocurre al frenar, al acelerar o si se escucha algún ruido/chillido)."
        return False, ""

    def _registrar_en_tracker(
        self, 
        placa: str, 
        marca_modelo: str, 
        sintoma: str, 
        diagnostico_ml: str, 
        campos_completos: int = 1
    ):
        """Registra el evento de diagnóstico en data/tracker_diagnosticos.csv si el archivo existe."""
        try:
            tracker_path = settings.TRACKER_PATH
            if os.path.exists(tracker_path):
                import datetime
                import csv
                import time
                fecha_hoy = datetime.date.today().isoformat()
                next_item = int(time.time())
                nueva_fila = [
                    next_item,
                    "Post-test",
                    fecha_hoy,
                    placa or "SIN-PLACA",
                    marca_modelo or "Generico",
                    sintoma,
                    diagnostico_ml,
                    diagnostico_ml,
                    campos_completos,
                    1,
                    1
                ]
                with _tracker_lock:
                    with open(tracker_path, mode='a', newline='', encoding='utf-8') as f:
                        writer = csv.writer(f)
                        writer.writerow(nueva_fila)
        except Exception as e:
            logger.warning(f"No se pudo registrar en tracker CSV: {e}")

    def procesar_consulta_texto(
        self, 
        texto_usuario: str, 
        placa: Optional[str] = None, 
        marca_modelo: Optional[str] = None, 
        session_id: Optional[str] = None
    ) -> str:
        """Flujo completo para consultas de texto (ML + RAG + LLM) con validación de ambigüedad y gestión de sesión (Slot-Filling)."""
        # Normalización de modismos y jerga mecánica peruana (ej: caña, cascabelea, se chupa, zapatea, etc.)
        texto_usuario = normalizar_jerga_peruana(texto_usuario)
        
        logger.info(
            f"Procesando consulta texto normalizada: '{texto_usuario}' | "
            f"Placa: {placa} | Marca/Modelo: {marca_modelo} | Session ID: {session_id}"
        )

        # 0. Validar si es un saludo / contacto inicial sin síntoma
        es_saludo, mensaje_saludo = self._es_saludo_o_contacto_inicial(texto_usuario)
        if es_saludo:
            if session_id:
                self.session_manager.obtener_o_crear_sesion(session_id)
            self.ultimo_diagnostico_ml = "Consulta General / Saludo"
            self.ultima_confianza = 1.0
            self.ultimo_contexto_manual = ""
            self.ultimo_titulo_manual = ""
            return mensaje_saludo

        # Identificar clave de sesión multiturno
        clave_sesion = session_id or (placa if placa not in (None, "REST-API", "WAPP-01") else None)

        if clave_sesion:
            sesion = self.session_manager.acumular_input_usuario(
                session_id=clave_sesion,
                texto_usuario=texto_usuario,
                placa=placa,
                marca_modelo=marca_modelo
            )
            texto_evaluar = sesion.obtener_sintoma_completo()
            marca_evaluar = marca_modelo or sesion.marca_modelo
            placa_evaluar = placa or sesion.placa
        else:
            texto_evaluar = texto_usuario
            marca_evaluar = marca_modelo
            placa_evaluar = placa

        # 0.1 Validar ambigüedad / datos faltantes (Requerimiento R1)
        es_ambigua, mensaje_aclaracion = self._es_consulta_ambigua(texto_evaluar)
        if es_ambigua:
            if clave_sesion:
                self.session_manager.obtener_o_crear_sesion(clave_sesion).estado = "esperando_clarificacion"
            self.ultimo_diagnostico_ml = "Consulta Ambigua / Datos Faltantes"
            self.ultima_confianza = 0.0
            self.ultimo_contexto_manual = ""
            self.ultimo_titulo_manual = ""
            return mensaje_aclaracion

        # 1. Clasificar con Machine Learning y obtener porcentaje de confianza
        diagnostico_predictivo, confianza = self.modelo_ml.predecir_falla_con_confianza(texto_evaluar)
        self.ultimo_diagnostico_ml = diagnostico_predictivo
        self.ultima_confianza = confianza
        
        # Si la confianza del modelo ML es sumamente baja (< 5%), no adivinar arbitrariamente
        if confianza < 0.05:
            self.ultimo_contexto_manual = ""
            self.ultimo_titulo_manual = ""
            return (
                "⚠️ **Síntoma no reconocido con suficiente certeza**\n\n"
                "El modelo de Machine Learning requiere una descripción un poco más detallada del síntoma.\n"
                "Por favor, indique si el problema se relaciona con los **frenos**, el **motor**, el **sistema de encendido/batería** o el **acelerador/mínimo**."
            )
        
        # 2. Recuperar del manual (RAG)
        contexto_manual, titulo_manual = self.motor_rag.recuperar_contexto(texto_evaluar)
        self.ultimo_contexto_manual = contexto_manual
        self.ultimo_titulo_manual = titulo_manual
        
        # 3. Generar la respuesta final estructurada en 3 secciones (Directa y concisa)
        respuesta_explicativa = self.generar_respuesta_conversacional(
            pregunta=texto_evaluar,
            diagnostico_ml=diagnostico_predictivo,
            confianza_ml=confianza,
            contexto_manual=contexto_manual,
            titulo_manual=titulo_manual
        )
        
        # Registrar en tracker CSV para trazabilidad del sistema
        self._registrar_en_tracker(
            placa=placa_evaluar or "DESCONOCIDO",
            marca_modelo=marca_evaluar or "Generico",
            sintoma=texto_evaluar,
            diagnostico_ml=diagnostico_predictivo,
            campos_completos=1
        )

        # Limpiar la sesión activa tras diagnóstico exitoso
        if clave_sesion:
            self.session_manager.reiniciar_sesion(clave_sesion)
        
        return respuesta_explicativa

    def procesar_consulta_audio(self, audio_id: str, datos_audio_vector = None) -> str:
        """Flujo completo para audios (Inactivo por ética por defecto, activable en .env para demo)."""
        habilitar_audio = os.getenv("HABILITAR_AUDIO", "false").lower() == "true"
        
        if not habilitar_audio:
            return (
                "🎙️ *Función de Audio Inactiva por Protocolo de Ética*\n\n"
                "Estimado usuario, para cumplir estrictamente con los protocolos de consentimiento, "
                "confidencialidad y protección de datos aprobados por el Comité de Ética de la universidad, "
                "el procesamiento directo de mensajes de voz y audio está inactivo en la versión oficial del sistema.\n\n"
                "Por favor, ✍️ *escriba los síntomas de su vehículo por mensaje de texto* para poder brindarle un diagnóstico automático asistido por Machine Learning y RAG."
            )
        
        frecuencia_simulada = 5200  # Hz
        energia_rms_simulada = 0.25
        t = np.linspace(0, 1, 44100)
        datos_simulados = np.sin(2 * np.pi * frecuencia_simulada * t) * energia_rms_simulada
        
        tipo_audio, diagnostico = self.procesador_audio.analizar_audio(datos_simulados)
        
        return (
            f"🎙️ **Análisis Acústico de Audio (Modo Demo Activo)**\n\n"
            f"• **Tipo de señal detectada:** {tipo_audio}\n"
            f"• **Energía RMS:** {energia_rms_simulada:.2f} (Señal estable)\n"
            f"• **Frecuencia dominante:** {frecuencia_simulada} Hz (Firma espectral de pastillas de freno)\n\n"
            f"🛠️ **1. Posible Falla Vehicular (Análisis Físico):** {diagnostico}\n\n"
            f"📖 **2. Procedimiento Técnico Recomendado:** Inspeccionar desgaste de discos y pastillas en el taller.\n\n"
            f"⏱️ **3. Tiempo Estimado:** 60 minutos | Gravedad: Alta"
        )

    def generar_respuesta_conversacional(
        self, 
        pregunta: str, 
        diagnostico_ml: str, 
        contexto_manual: str, 
        confianza_ml: float = 0.85, 
        titulo_manual: str = ""
    ) -> str:
        """Envía el prompt aumentado con RAG y clasificación ML a la API de Gemini con REGLA ESTRICTA DE VEREDICTO ÚNICO."""
        confianza_pct = int(confianza_ml * 100)
        
        prompt_sistema = f"""
        Eres 'CarBot', el asistente técnico de diagnóstico de precisión para mecánicos de taller automotriz.

        INFORMACIÓN CLAVE DE IA:
        - Diagnóstico Principal (Machine Learning): {diagnostico_ml} (Confianza del modelo: {confianza_pct}%)
        - Manual Técnico Recuperado (RAG): [{titulo_manual}]
        {contexto_manual}
        
        Consulta técnica del usuario: "{pregunta}"
        
        REGLAS ESTRICTAS DE RESPUESTA:
        1. SÉ TOTALMENTE DIRECTO Y CONCISO. NO DES LISTAS DE 5 O 6 ALTERNATIVAS NUNCA.
        2. Enfócate EXCLUSIVAMENTE en el Diagnóstico Principal predicho por el modelo ML ({diagnostico_ml}).
        3. Estructura la respuesta EXACTAMENTE en las siguientes 3 secciones:

        🛠️ **1. Posible Falla Vehicular**
        Indica únicamente el diagnóstico principal ({diagnostico_ml}) y su nivel de confianza ({confianza_pct}%).

        📖 **2. Procedimiento Técnico de Reparación**
        Paso a paso exacto extraído del manual de taller RAG.

        ⏱️ **3. Tiempo Estimado y Gravedad**
        Indica el tiempo estimado de trabajo en taller y nivel de urgencia.
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
                logger.error(f"Error al consultar la API de Gemini: {e}")
                
        # Fallback local conversacional estandarizado en 3 secciones directo y sin alternativas redundantes
        no_manual = "No se encontró" in contexto_manual or "Coincidencia baja" in titulo_manual
        
        seccion_1 = f"🛠️ **1. Posible Falla Vehicular:**\n• **Diagnóstico Sugerido (ML):** {diagnostico_ml}\n• **Certeza del Modelo:** {confianza_pct}%"
        
        if no_manual:
            seccion_2 = "📖 **2. Procedimiento Técnico de Reparación:**\n⚠️ *Nota:* No se encontró un procedimiento específico en el manual de taller para esta consulta. Se sugiere revisión visual directa."
            seccion_3 = "⏱️ **3. Tiempo Estimado y Gravedad:**\n• **Tiempo Estimado:** 30-45 minutos (Evaluación inicial)\n• **Gravedad:** Por determinar en taller"
        else:
            seccion_2 = f"📖 **2. Procedimiento Técnico de Reparación ({titulo_manual}):**\n{contexto_manual}"
            seccion_3 = "⏱️ **3. Tiempo Estimado y Gravedad:**\n• **Recomendación Técnica:** Siga los pasos del manual de taller adjunto y realice las pruebas de verificación correspondientes."
            
        return f"{seccion_1}\n\n{seccion_2}\n\n{seccion_3}"
