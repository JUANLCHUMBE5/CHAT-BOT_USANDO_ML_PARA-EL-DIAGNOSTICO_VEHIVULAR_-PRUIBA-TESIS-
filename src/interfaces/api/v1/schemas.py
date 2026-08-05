from pydantic import BaseModel, Field
from typing import Optional, List

# --- DTOs de Entrada (Request Schemas) ---

class SymptomRequestDTO(BaseModel):
    sintoma: str = Field(..., example="siento un chillido feo al frenar el carro", description="Texto con la descripción del síntoma o problema del auto")
    marca: Optional[str] = Field(default="Generico", example="Toyota", description="Marca del vehículo")
    modelo: Optional[str] = Field(default="Generico", example="Yaris", description="Modelo del vehículo")
    anio: Optional[int] = Field(default=2015, example=2018, description="Año de fabricación del vehículo")
    placa: Optional[str] = Field(default=None, example="ABC-123", description="Placa del vehículo")
    session_id: Optional[str] = Field(default=None, example="sess-12345", description="ID de sesión para el seguimiento conversacional")

class WhatsAppWebhookPayloadDTO(BaseModel):
    from_number: str = Field(..., example="whatsapp:+51987654321", description="Número remitente del WhatsApp")
    message_type: str = Field(default="text", example="text", description="Tipo de entrada: text o audio")
    body_text: Optional[str] = Field(default=None, description="Texto enviado en la consulta")
    media_url: Optional[str] = Field(default=None, description="URL del archivo multimedia/audio si aplica")

# --- DTOs de Salida (Response Schemas) ---

class DiagnosticResponseDTO(BaseModel):
    sintoma: str = Field(..., description="Síntoma o consulta ingresada por el usuario")
    falla_predicha: str = Field(..., description="Falla vehicular estimada por el modelo ML")
    confianza: float = Field(..., example=95.5, description="Porcentaje de confianza del diagnóstico (0-100)")
    requiere_revision_humana: bool = Field(default=False, description="Flag que indica si la confianza es baja y requiere mecánico")
    procedimiento_tecnico: Optional[str] = Field(default=None, description="Pasos de reparación recuperados del manual técnico vía RAG")
    respuesta_explicativa: Optional[str] = Field(default=None, description="Respuesta completa sintetizada por Gemini o plantilla de 3 secciones")
    tiempo_respuesta_ms: float = Field(..., description="Tiempo total de procesamiento en milisegundos")

class HealthCheckDTO(BaseModel):
    status: str = "healthy"
    app_name: str
    version: str

# Aliases de compatibilidad directa
ConsultaDiagnostico = SymptomRequestDTO
ResultadoDiagnostico = DiagnosticResponseDTO
