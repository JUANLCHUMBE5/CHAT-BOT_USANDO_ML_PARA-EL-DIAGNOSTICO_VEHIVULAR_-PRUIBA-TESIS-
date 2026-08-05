import time
from fastapi import APIRouter, HTTPException
from fastapi.concurrency import run_in_threadpool
from src.interfaces.api.v1.schemas import ConsultaDiagnostico, ResultadoDiagnostico
from src.core.gestor_diagnostico import GestorDiagnostico
from src.core.logger import logger
from src.config import settings

# Crear enrutador FastAPI para diagnóstico general
router = APIRouter()

# Instanciar el orquestador core de diagnóstico
gestor = GestorDiagnostico()

@router.post("/analizar", response_model=ResultadoDiagnostico)
async def analizar_sintoma(consulta: ConsultaDiagnostico):
    """
    Endpoint general para analizar un síntoma mecánico y obtener un diagnóstico híbrido.
    Ideal para ser consumido por una aplicación web externa, app móvil o panel de administración.
    """
    if not consulta.sintoma.strip():
        raise HTTPException(status_code=400, detail="El síntoma no puede estar vacío.")

    t_inicio = time.time()
    try:
        logger.info(f"Procesando petición HTTP REST para síntoma: {consulta.sintoma}")
        
        marca_modelo = f"{consulta.marca} {consulta.modelo}".strip()
        placa_val = consulta.placa or "REST-API"
        respuesta_explicativa = await run_in_threadpool(
            gestor.procesar_consulta_texto,
            consulta.sintoma, 
            placa=placa_val, 
            marca_modelo=marca_modelo,
            session_id=consulta.session_id
        )
        
        t_final = time.time()
        elapsed_ms = (t_final - t_inicio) * 1000

        diagnostico_ml = getattr(gestor, 'ultimo_diagnostico_ml', "Diagnóstico Vehicular")
        confianza = getattr(gestor, 'ultima_confianza', 1.0)
        contexto_manual = getattr(gestor, 'ultimo_contexto_manual', "")

        confianza_pct = round(confianza * 100, 2)
        requiere_revision = confianza < settings.diagnostic.confidence_threshold

        return ResultadoDiagnostico(
            sintoma=consulta.sintoma,
            falla_predicha=diagnostico_ml,
            confianza=confianza_pct,
            requiere_revision_humana=requiere_revision,
            procedimiento_tecnico=contexto_manual,
            respuesta_explicativa=respuesta_explicativa,
            tiempo_respuesta_ms=round(elapsed_ms, 2)
        )
    except Exception as e:
        logger.error(f"Error al procesar diagnóstico en API REST: {e}")
        raise HTTPException(status_code=500, detail="Error interno al procesar el diagnóstico.")

