import os
from pathlib import Path
from pydantic import BaseModel, Field

# Base Directory of the Project
BASE_DIR = Path(__file__).resolve().parent.parent

class PathConfig(BaseModel):
    data_dir: Path = BASE_DIR / "data"
    dataset_csv: Path = BASE_DIR / "data" / "dataset_sintomas.csv"
    tracker_csv: Path = BASE_DIR / "data" / "tracker_diagnosticos.csv"
    manuals_dir: Path = BASE_DIR / "manuales_taller"
    manual_file: Path = BASE_DIR / "manuales_taller" / "manual_procedimientos.txt"
    model_pkl: Path = BASE_DIR / "models" / "modelo_diagnostico.pkl"
    vectorizer_pkl: Path = BASE_DIR / "models" / "vectorizador_tfidf.pkl"
    temp_audio: Path = BASE_DIR / "grabacion.wav"

class DiagnosticConfig(BaseModel):
    confidence_threshold: float = Field(default=0.70, description="Umbral mínimo de confianza para diagnóstico automático")
    rms_silence_threshold: float = Field(default=0.01, description="Umbral de energía RMS para detectar silencio")
    treble_ratio_threshold: float = Field(default=15.0, description="Porcentaje de frecuencias agudas (>2000Hz) para ruido mecánico")

class AppSettings(BaseModel):
    app_name: str = "Chatbot Diagnostico Vehicular ML+RAG"
    version: str = "1.0.0"
    description: str = "Chatbot utilizando machine learning para el diagnóstico vehicular en talleres mecánicos de Carabayllo"
    debug: bool = True
    environment: str = os.getenv("ENVIRONMENT", "development")
    port: int = int(os.getenv("PORT", 8000))
    ngrok_domain: str = os.getenv("NGROK_DOMAIN", "")
    
    # API Keys & Credentials
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    twilio_account_sid: str = os.getenv("TWILIO_ACCOUNT_SID", "")
    twilio_auth_token: str = os.getenv("TWILIO_AUTH_TOKEN", "")
    verify_token: str = os.getenv("VERIFY_TOKEN", "MI_TOKEN_DE_VERIFICACION_SEC_123")
    token_whatsapp: str = os.getenv("TOKEN_WHATSAPP", "")
    telefono_id: str = os.getenv("TELEFONO_ID", "")

    # Sub-configuraciones
    paths: PathConfig = Field(default_factory=PathConfig)
    diagnostic: DiagnosticConfig = Field(default_factory=DiagnosticConfig)

    # Aliases de compatibilidad directa (Mayúsculas y Minúsculas)
    @property
    def PROJECT_NAME(self) -> str:
        return self.app_name

    @property
    def DESCRIPTION(self) -> str:
        return self.description

    @property
    def VERSION(self) -> str:
        return self.version

    @property
    def PORT(self) -> int:
        return self.port

    @property
    def NGROK_DOMAIN(self) -> str:
        return self.ngrok_domain

    @property
    def MODELO_ML_PATH(self) -> str:
        return str(self.paths.model_pkl)

    @property
    def VECTORIZADOR_PATH(self) -> str:
        return str(self.paths.vectorizer_pkl)

    @property
    def VECTORIZADOR_TFIDF_PATH(self) -> str:
        return str(self.paths.vectorizer_pkl)

    @property
    def MANUAL_PATH(self) -> str:
        return str(self.paths.manual_file)

    @property
    def MANUAL_TALLER_PATH(self) -> str:
        return str(self.paths.manual_file)

    @property
    def MANUAL_PROCEDIMIENTOS_PATH(self) -> str:
        return str(self.paths.manual_file)

    @property
    def TRACKER_PATH(self) -> str:
        return str(self.paths.tracker_csv)

    @property
    def DATASET_PATH(self) -> str:
        return str(self.paths.dataset_csv)

    @property
    def GEMINI_API_KEY(self) -> str:
        return self.gemini_api_key

    @property
    def OPENAI_API_KEY(self) -> str:
        return self.openai_api_key

    @property
    def TWILIO_ACCOUNT_SID(self) -> str:
        return self.twilio_account_sid

    @property
    def TWILIO_AUTH_TOKEN(self) -> str:
        return self.twilio_auth_token

    @property
    def VERIFY_TOKEN(self) -> str:
        return self.verify_token

    @property
    def TOKEN_WHATSAPP(self) -> str:
        return self.token_whatsapp

    @property
    def TELEFONO_ID(self) -> str:
        return self.telefono_id

# Instancia global de configuración centralizada
settings = AppSettings()
