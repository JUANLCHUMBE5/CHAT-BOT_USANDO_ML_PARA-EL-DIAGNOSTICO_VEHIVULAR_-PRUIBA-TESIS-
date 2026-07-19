import os

# Cargar variables de entorno desde archivo .env local si existe (evita configurar variables en terminal)
if os.path.exists(".env"):
    with open(".env", "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                key, val = line.split("=", 1)
                os.environ[key.strip()] = val.strip().strip('"').strip("'")

from fastapi import FastAPI
import uvicorn
from src.interfaces.api.v1.router import api_router

# Inicializar aplicación FastAPI con soporte modular y versionamiento
app = FastAPI(
    title="Chatbot Vehicular - Arquitectura Modular en Capas",
    description="Implementación de la arquitectura híbrida modular (ML + RAG + LLM) estructurada por capas y rutas para sustentación de tesis.",
    version="1.0.0"
)

# Incluir las rutas modulares versionadas bajo /api/v1
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {
        "estado": "online",
        "sistema": "Chatbot de Diagnóstico Vehicular Híbrido Modular",
        "taller": "Taller Mecánico en Carabayllo",
        "documentacion": "Módulos de la arquitectura modular cargados correctamente: Presentación (api/v1), Aplicación, Infraestructura."
    }

if __name__ == "__main__":
    # Arrancar el servidor en el puerto 8000
    # Ejecución: python main.py
    port = int(os.getenv("PORT", 8000))
    print(f"🚀 Iniciando servidor del Chatbot Vehicular en el puerto {port}...")
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)

