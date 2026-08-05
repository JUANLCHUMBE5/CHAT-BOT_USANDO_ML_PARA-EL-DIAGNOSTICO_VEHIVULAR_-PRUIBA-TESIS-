import sys
import subprocess
from fastapi import FastAPI
import uvicorn
from src.interfaces.api.v1.router import api_router
from src.config import settings
from src.core.logger import logger

# Forzar codificación UTF-8 en consolas de Windows para evitar errores de emojis
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Inicializar aplicación FastAPI con soporte modular y versionamiento
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.DESCRIPTION,
    version=settings.VERSION
)

# Incluir las rutas modulares versionadas bajo /api/v1
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {
        "estado": "online",
        "sistema": settings.PROJECT_NAME,
        "taller": "Taller Mecánico en Carabayllo",
        "documentacion": "Módulos de la arquitectura modular cargados correctamente: Presentación (api/v1), Aplicación, Infraestructura."
    }

def _iniciar_ngrok_autonomo(puerto: int, dominio: str):
    """Arranca automáticamente el túnel de Ngrok en segundo plano con tu dominio estático."""
    try:
        comando = f"ngrok http --domain={dominio} {puerto}"
        subprocess.Popen(comando, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        logger.info(f"Túnel estático Ngrok activado: https://{dominio}")
        logger.info(f"URL de Webhook WhatsApp para Meta: https://{dominio}/api/v1/webhook")
    except Exception as e:
        logger.warning(f"No se pudo iniciar el túnel automático de Ngrok: {e}")

if __name__ == "__main__":
    if settings.NGROK_DOMAIN:
        _iniciar_ngrok_autonomo(settings.PORT, settings.NGROK_DOMAIN)
        
    logger.info(f"Iniciando servidor del Chatbot Vehicular en el puerto {settings.PORT}...")
    uvicorn.run("main:app", host="0.0.0.0", port=settings.PORT, reload=True)
