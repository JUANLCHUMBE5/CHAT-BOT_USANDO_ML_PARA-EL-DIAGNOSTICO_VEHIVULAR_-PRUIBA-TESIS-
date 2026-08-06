import sys
import os
import subprocess
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI, Request
import uvicorn

# Cargar variables de entorno automáticamente desde .env
load_dotenv()

from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from src.limiter import limiter
from src.interfaces.api.v1.router import api_router
from src.core.gestor_diagnostico import GestorDiagnostico
from src.config import settings
from src.core.logger import logger

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gestor de Ciclo de Vida de FastAPI (Singleton).
    Carga el GestorDiagnostico, Modelo ML (540MB) y FAISS RAG 1 SOLA VEZ en app.state para todos los workers.
    """
    settings.validar_seguridad_produccion()
    logger.info("Cargando GestorDiagnostico (Modelo ML + FAISS RAG) 1 sola vez en el estado de la app...")
    app.state.gestor_diagnostico = GestorDiagnostico()
    logger.info("¡Instancia global Singleton cargada exitosamente!")
    yield
    logger.info("Cerrando recursos de la aplicación...")


# Inicializar aplicación FastAPI con soporte modular y versionamiento
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.DESCRIPTION,
    version=settings.VERSION,
    lifespan=lifespan
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# Incluir las rutas modulares versionadas bajo /api/v1
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {
        "estado": "online",
        "sistema": settings.PROJECT_NAME,
        "taller": "Taller Mecánico en Carabayllo",
        "seguridad": "JWT Bearer Token (2 Horas Exp.) + Validación Firma HMAC + Rate Limiting + Concurrencia Thread-Safe",
        "documentacion": "Módulos de la arquitectura modular cargados correctamente: Presentación (api/v1), Aplicación, Infraestructura."
    }

def _iniciar_ngrok_autonomo(puerto: int, dominio: str):
    """Arranca automáticamente el túnel de Ngrok en segundo plano con tu dominio estático sin shell=True."""
    try:
        comando = ["ngrok", "http", f"--domain={dominio}", str(puerto)]
        subprocess.Popen(comando, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        logger.info(f"Túnel estático Ngrok activado: https://{dominio}")
        logger.info(f"URL de Webhook WhatsApp para Meta: https://{dominio}/api/v1/webhook")
    except Exception as e:
        logger.warning(f"No se pudo iniciar el túnel automático de Ngrok: {e}")

if __name__ == "__main__":
    if settings.NGROK_DOMAIN:
        _iniciar_ngrok_autonomo(settings.PORT, settings.NGROK_DOMAIN)
        
    logger.info(f"Iniciando servidor del Chatbot Vehicular en el puerto {settings.PORT}...")
    uvicorn.run("main:app", host="0.0.0.0", port=settings.PORT, reload=False)
