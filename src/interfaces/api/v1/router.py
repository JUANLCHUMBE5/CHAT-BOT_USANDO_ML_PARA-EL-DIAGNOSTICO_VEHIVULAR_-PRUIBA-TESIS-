from fastapi import APIRouter
from src.interfaces.api.v1.endpoints.webhook import router as webhook_router
from src.interfaces.api.v1.endpoints.diagnostico import router as diagnostico_router

# Crear router principal para v1
api_router = APIRouter()

# Registrar sub-enrutadores modulares
api_router.include_router(webhook_router, prefix="/webhook", tags=["Webhook WhatsApp"])
api_router.include_router(diagnostico_router, prefix="/diagnostico", tags=["Diagnóstico REST"])
