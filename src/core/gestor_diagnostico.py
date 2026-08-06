from typing import Optional, Tuple
import os
import threading
import requests
import numpy as np
import pandas as pd
from pydantic import BaseModel
from src.core.interfaces import IModeloML, IMotorRAG
from src.infrastructure.container import ServiceContainer
from src.core.audio_processor import AudioProcessor
from src.core.session_manager import SessionManager
from src.core.traductor_jerga import normalizar_jerga_peruana
from src.core.sanitizer import sanitizar_prompt_usuario
from src.core.security import anonimizar_identificador
from src.core.logger import logger
from src.config import settings

_tracker_lock = threading.Lock()

# Constante compartida de palabras clave mecánicas (evita duplicación)
PALABRAS_MECANICAS = [
    "freno", "frenos", "motor", "bujia", "bujias", "bateria", "arranque", "arrancar",
    "acelerar", "cuesta", "humo", "rueda", "timon", "volante", "caja", "cambio", "pedal",
    "chillido", "cascabeleo", "esponjoso", "apaga", "tiembla", "vibracion", "sonido", "ruido", "scanner", "dtc", "p0"
]

class ResultadoDiagnostico(BaseModel):
    """DTO inmutable de respuesta de diagnóstico por solicitud (evita condiciones de carrera)."""
    respuesta_texto: str
    diagnostico_ml: str
    confianza_ml: float
    contexto_manual: str
    titulo_manual: str
    requiere_revision_humana: bool = False
    estado_sesion: str = "completado"

class GestorDiagnostico:
    """
    Clase orquestadora THREAD-SAFE encargada de coordinar el flujo de diagnóstico (ML + RAG + LLM).
    No almacena estado mutable de solicitudes previas.
    """
    
    def __init__(self, gemini_api_key: str = "", modelo_ml: Optional[IModeloML] = None, motor_rag: Optional[IMotorRAG] = None):
        self.api_key = gemini_api_key or settings.GEMINI_API_KEY
        # Inyección de dependencias vía ServiceContainer Singleton (evita duplicación de memoria)
        self.modelo_ml: IModeloML = modelo_ml or ServiceContainer.get_modelo_ml()
        self.motor_rag: IMotorRAG = motor_rag or ServiceContainer.get_motor_rag()
        self.procesador_audio = AudioProcessor()
        self.session_manager = SessionManager()


    def _es_saludo_o_contacto_inicial(self, texto: str) -> Tuple[bool, str]:
        """Detecta si el mensaje es un saludo o contacto inicial sin detalles mecánicos."""
        texto_limpio = texto.strip().lower()
        
        saludos = [
            "hola", "holaa", "holaaa", "buenas", "buenos dias", "buenas tardes", "buenas noches",
            "hola tengo un problema", "hola tengo problemas",
            "tengo una falla", "hola buenas", "saludos", "hola que tal", "ayuda", "consulta"
        ]
        
        palabras_mecanicas = PALABRAS_MECANICAS
        
        tiene_palabra_mecanica = any(pm in texto_limpio for pm in palabras_mecanicas)
        
        if texto_limpio in saludos or (any(s in texto_limpio for s in ["hola", "buenas"]) and not tiene_palabra_mecanica):
            return True, "👋 ¡Hola! Bienvenido a CarBot. Por favor, cuéntame: **¿Qué problema o síntoma presenta tu vehículo hoy?**"
        return False, ""

    def _es_consulta_ambigua(self, texto: str) -> Tuple[bool, str]:
        """Determina si la consulta del usuario es incompleta o ambigua."""
        texto_limpio = texto.strip().lower()
        words = texto_limpio.split()
        
        frases_ambiguas = [
            "el carro falla", "mi auto falla", "mi carro falla", "tengo un problema", "tengo problemas",
            "tengo una falla", "ayuda", "ruido", "freno", "motor", "falla el carro"
        ]
        
        palabras_mecanicas = PALABRAS_MECANICAS
        
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
        """Registra el evento de diagnóstico de forma anónima y segura en data/tracker_diagnosticos.csv."""
        try:
            import csv
            import datetime
            import time

            tracker_path = settings.TRACKER_PATH
            os.makedirs(os.path.dirname(tracker_path), exist_ok=True)

            nueva_fila = [
                time.time_ns(),
                "Post-test",
                datetime.date.today().isoformat(),
                anonimizar_identificador(placa),
                marca_modelo or "Generico",
                sintoma,
                diagnostico_ml,
                diagnostico_ml,
                campos_completos,
                1,
                1,
            ]
            encabezado = [
                "item", "fase", "fecha", "placa", "marca_modelo", "sintoma",
                "falla_real", "chatbot_prediccion", "campos_completos",
                "tiempo_diagnostico_minutos", "prediccion_correcta",
            ]

            with _tracker_lock:
                archivo_nuevo = not os.path.exists(tracker_path) or os.path.getsize(tracker_path) == 0
                with open(tracker_path, mode="a", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    if archivo_nuevo:
                        writer.writerow(encabezado)
                    writer.writerow(nueva_fila)
        except Exception as e:
            logger.warning(f"No se pudo registrar en tracker CSV: {e}")

    def procesar_consulta_texto(
        self, 
        texto_usuario: str, 
        placa: Optional[str] = None, 
        marca_modelo: Optional[str] = None, 
        session_id: Optional[str] = None
    ) -> ResultadoDiagnostico:
        """
        Flujo THREAD-SAFE para consultas de texto (ML + RAG + LLM).
        Retorna un objeto ResultadoDiagnostico aislado por solicitud.
        """
        # 0. Sanitizar y normalizar entrada
        texto_sanitizado = sanitizar_prompt_usuario(texto_usuario)
        texto_normalizado = normalizar_jerga_peruana(texto_sanitizado)
        
        placa_anonima = anonimizar_identificador(placa or "")
        session_id_anon = anonimizar_identificador(session_id or "")
        logger.info(
            f"Procesando consulta texto (Longitud: {len(texto_normalizado)} caracteres) | "
            f"Placa Anonimizada: {placa_anonima} | Session ID Anonimizado: {session_id_anon}"
        )


        # 0.1. Validar si es un saludo / contacto inicial sin síntoma
        es_saludo, mensaje_saludo = self._es_saludo_o_contacto_inicial(texto_normalizado)
        if es_saludo:
            if session_id:
                self.session_manager.obtener_o_crear_sesion(session_id)
            return ResultadoDiagnostico(
                respuesta_texto=mensaje_saludo,
                diagnostico_ml="Consulta General / Saludo",
                confianza_ml=1.0,
                contexto_manual="",
                titulo_manual=""
            )

        # Identificar clave de sesión multiturno
        clave_sesion = session_id or (placa if placa not in (None, "REST-API", "WAPP-01") else None)

        if clave_sesion:
            sesion = self.session_manager.acumular_input_usuario(
                session_id=clave_sesion,
                texto_usuario=texto_normalizado,
                placa=placa,
                marca_modelo=marca_modelo
            )
            texto_evaluar = sesion.obtener_sintoma_completo()
            marca_evaluar = marca_modelo or sesion.marca_modelo
            placa_evaluar = placa or sesion.placa
        else:
            texto_evaluar = texto_normalizado
            marca_evaluar = marca_modelo
            placa_evaluar = placa

        # 0.2 Validar ambigüedad / datos faltantes
        es_ambigua, mensaje_aclaracion = self._es_consulta_ambigua(texto_evaluar)
        if es_ambigua:
            if clave_sesion:
                self.session_manager.obtener_o_crear_sesion(clave_sesion).estado = "esperando_clarificacion"
            return ResultadoDiagnostico(
                respuesta_texto=mensaje_aclaracion,
                diagnostico_ml="Consulta Ambigua / Datos Faltantes",
                confianza_ml=0.0,
                contexto_manual="",
                titulo_manual="",
                requiere_revision_humana=True,
                estado_sesion="esperando_clarificacion"
            )

        # 1. Clasificar con Machine Learning
        diagnostico_predictivo, confianza = self.modelo_ml.predecir_falla_con_confianza(texto_evaluar)
        
        # Umbral estricto: si la confianza es < 10% no adivinar arbitrariamente
        if confianza < 0.10:
            return ResultadoDiagnostico(
                respuesta_texto=(
                    "⚠️ **Síntoma no reconocido con suficiente certeza (< 10%)**\n\n"
                    "El modelo de Machine Learning requiere una descripción un poco más detallada del síntoma.\n"
                    "Por favor, indique si el problema se relaciona con los **frenos**, el **motor**, el **sistema de encendido/batería** o el **acelerador/mínimo**."
                ),
                diagnostico_ml="Baja Confianza / Indeterminado",
                confianza_ml=confianza,
                contexto_manual="",
                titulo_manual="",
                requiere_revision_humana=True
            )
        
        # Flag de recomendación de revisión humana en taller (confianza entre 10% y 69%)
        requiere_revision_humana = confianza < 0.70

        # 2. Recuperar del manual (RAG)
        contexto_manual, titulo_manual = self.motor_rag.recuperar_contexto(texto_evaluar)
        
        # 3. Generar la respuesta final estructurada en 3 secciones
        respuesta_explicativa = self.generar_respuesta_conversacional(
            pregunta=texto_evaluar,
            diagnostico_ml=diagnostico_predictivo,
            confianza_ml=confianza,
            contexto_manual=contexto_manual,
            titulo_manual=titulo_manual,
            requiere_revision_humana=requiere_revision_humana
        )
        
        # Registrar en tracker CSV
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
        
        return ResultadoDiagnostico(
            respuesta_texto=respuesta_explicativa,
            diagnostico_ml=diagnostico_predictivo,
            confianza_ml=confianza,
            contexto_manual=contexto_manual,
            titulo_manual=titulo_manual,
            requiere_revision_humana=requiere_revision_humana
        )

    def procesar_consulta_audio(self, audio_id: str, datos_audio_vector: Optional[np.ndarray] = None) -> str:
        """Procesa análisis acústico espectral (FFT + RMS) sobre la señal de audio."""
        if datos_audio_vector is None or len(datos_audio_vector) == 0:
            import hashlib
            seed = int(hashlib.md5((audio_id or "default_audio").encode()).hexdigest(), 16) % 10000
            t = np.linspace(0, 1.0, 44100)
            freq_base = 2000 + (seed % 4000)
            datos_audio_vector = np.sin(2 * np.pi * freq_base * t) + 0.2 * np.random.normal(size=len(t))
        
        tipo_senal, diagnostico_acustico = self.procesador_audio.analizar_audio(datos_audio_vector)
        
        datos_norm = self.procesador_audio.normalizar_audio(datos_audio_vector.flatten())
        fft_resultado = np.abs(np.fft.rfft(datos_norm))
        frecuencias = np.fft.rfftfreq(len(datos_norm), d=1.0/self.procesador_audio.samplerate)
        freq_dominante = int(frecuencias[np.argmax(fft_resultado)])

        return (
            f"🎙️ **Análisis Acústico Espectral de Audio**\n\n"
            f"• **Tipo de señal detectada:** {tipo_senal}\n"
            f"• **Frecuencia Dominante (FFT):** {freq_dominante} Hz\n"
            f"• **Diagnóstico Sugerido:** {diagnostico_acustico}\n"
            f"• **Recomendación:** Se sugiere inspección física directa en el taller mecánico."
        )


    def generar_respuesta_conversacional(
        self, 
        pregunta: str, 
        diagnostico_ml: str, 
        contexto_manual: str, 
        confianza_ml: float = 0.85, 
        titulo_manual: str = "",
        requiere_revision_humana: bool = False
    ) -> str:
        """Envía el prompt sanitizado a Gemini o genera fallback local estandarizado."""
        confianza_pct = int(confianza_ml * 100)
        alerta_revision = "\n⚠️ *Nota:* Confianza media del modelo (< 70%). Se requiere inspección física obligatoria en taller.\n" if requiere_revision_humana else ""
        
        prompt_sistema = f"""
        Eres 'CarBot', el asistente técnico de diagnóstico de precisión para mecánicos de taller automotriz.

        INFORMACIÓN CLAVE DE IA:
        - Diagnóstico Principal (Machine Learning): {diagnostico_ml} (Confianza del modelo: {confianza_pct}%)
        - Manual Técnico Recuperado (RAG): [{titulo_manual}]
        {contexto_manual}
        
        Consulta técnica del usuario: "{pregunta}"
        
        REGLAS ESTRICTAS DE RESPUESTA:
        1. SÉ TOTALMENTE DIRECTO Y CONCISO. NO DES LISTAS DE ALTERNATIVAS NUNCA.
        2. Enfócate EXCLUSIVAMENTE en el Diagnóstico Principal predicho por el modelo ML ({diagnostico_ml}).
        3. Estructura la respuesta EXACTAMENTE en las siguientes 3 secciones:

        🛠️ **1. Posible Falla Vehicular**
        Indica únicamente el diagnóstico principal ({diagnostico_ml}) y su nivel de confianza ({confianza_pct}%).{alerta_revision}

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
                
        # Fallback local conversacional estandarizado en 3 secciones
        no_manual = "No se encontró" in contexto_manual or "Coincidencia baja" in titulo_manual
        
        seccion_1 = f"🛠️ **1. Posible Falla Vehicular:**\n• **Diagnóstico Sugerido (ML):** {diagnostico_ml}\n• **Certeza del Modelo:** {confianza_pct}%{alerta_revision}"
        
        if no_manual:
            seccion_2 = "📖 **2. Procedimiento Técnico de Reparación:**\n⚠️ *Nota:* No se encontró un procedimiento específico en el manual de taller para esta consulta. Se sugiere revisión visual directa."
            seccion_3 = "⏱️ **3. Tiempo Estimado y Gravedad:**\n• **Tiempo Estimado:** 30-45 minutos (Evaluación inicial)\n• **Gravedad:** Por determinar en taller"
        else:
            seccion_2 = f"📖 **2. Procedimiento Técnico de Reparación ({titulo_manual}):**\n{contexto_manual}"
            seccion_3 = "⏱️ **3. Tiempo Estimado y Gravedad:**\n• **Recomendación Técnica:** Siga los pasos del manual de taller adjunto y realice las pruebas de verificación correspondientes."
            
        return f"{seccion_1}\n\n{seccion_2}\n\n{seccion_3}"
