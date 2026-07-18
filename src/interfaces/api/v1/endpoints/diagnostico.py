from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from src.core.gestor_diagnostico import GestorDiagnostico

# Crear enrutador FastAPI para diagnóstico general
router = APIRouter()

# Instanciar el orquestador core de diagnóstico
gestor = GestorDiagnostico()

class ConsultaDiagnostico(BaseModel):
    sintoma: str = Field(..., description="El síntoma técnico que reporta el cliente sobre su vehículo", example="Siento que el pedal de freno vibra bastante al frenar")

class ResultadoDiagnostico(BaseModel):
    sintoma: str
    diagnostico_ml: str = Field(..., description="Categoría de falla detectada por el modelo de Machine Learning")
    manual_recuperado: str = Field(..., description="Instrucciones técnicas extraídas del manual del taller (RAG)")
    respuesta_explicativa: str = Field(..., description="Respuesta conversacional explicativa final para el usuario")

@router.post("/analizar", response_model=ResultadoDiagnostico)
def analizar_sintoma(consulta: ConsultaDiagnostico):
    """
    Endpoint general para analizar un síntoma mecánico y obtener un diagnóstico híbrido.
    Ideal para ser consumido por una aplicación web externa, app móvil o panel de administración.
    """
    if not consulta.sintoma.strip():
        raise HTTPException(status_code=400, detail="El síntoma no puede estar vacío.")

    try:
        # 1. Obtener la predicción de Machine Learning clasificada
        diagnostico_ml = gestor.modelo_ml.predecir_falla(consulta.sintoma)
        
        # 2. Recuperar el manual del RAG
        contexto_manual, _ = gestor.motor_rag.recuperar_contexto(consulta.sintoma)
        
        # 3. Generar la respuesta conversacional explicativa
        respuesta_explicativa = gestor.generar_respuesta_conversacional(
            pregunta=consulta.sintoma,
            diagnostico_ml=diagnostico_ml,
            contexto_manual=contexto_manual
        )
        
        return ResultadoDiagnostico(
            sintoma=consulta.sintoma,
            diagnostico_ml=diagnostico_ml,
            manual_recuperado=contexto_manual,
            respuesta_explicativa=respuesta_explicativa
        )
    except Exception as e:
        print(f"❌ Error al procesar diagnóstico en API REST: {e}")
        raise HTTPException(status_code=500, detail="Error interno al procesar el diagnóstico.")
