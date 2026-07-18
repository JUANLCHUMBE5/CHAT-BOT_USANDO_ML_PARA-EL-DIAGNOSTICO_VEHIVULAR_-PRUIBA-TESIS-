import os
from fastapi import FastAPI
import uvicorn
from src.interfaces.webhook import router as whatsapp_router

# Inicializar aplicación FastAPI
app = FastAPI(
    title="Chatbot Vehicular - Arquitectura en Capas",
    description="Implementación oficial de la arquitectura híbrida (ML + RAG + LLM) estructurada en capas para sustentación de tesis.",
    version="1.0.0"
)

# Incluir las rutas de WhatsApp
app.include_router(whatsapp_router)

@app.get("/")
def read_root():
    return {
        "estado": "online",
        "sistema": "Chatbot de Diagnóstico Vehicular Híbrido",
        "taller": "Taller Mecánico en Carabayllo",
        "documentacion": "Módulos de la arquitectura cargados correctamente: Presentación, Aplicación, Infraestructura."
    }

if __name__ == "__main__":
    # Arrancar el servidor en el puerto 8000
    # Ejecución: python main.py
    port = int(os.getenv("PORT", 8000))
    print(f"🚀 Iniciando servidor del Chatbot Vehicular en el puerto {port}...")
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
