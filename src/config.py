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
    meta_verify_token: str = os.getenv("META_VERIFY_TOKEN", os.getenv("VERIFY_TOKEN", "MI_TOKEN_DE_VERIFICACION_SEC_123"))
    meta_app_secret: str = os.getenv("META_APP_SECRET", "")
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "super_secret_carbot_key_ucv_2026_carabayllo")
    token_whatsapp: str = os.getenv("TOKEN_WHATSAPP", "")
    telefono_id: str = os.getenv("TELEFONO_ID", "")

    privacy_secret_key: str = os.getenv("PRIVACY_SECRET_KEY", "carbot_privacy_hmac_secret_key_2026")

    # Credenciales de autenticación JWT (configurables vía .env)
    auth_username: str = os.getenv("AUTH_USERNAME", "admin")
    auth_password: str = os.getenv("AUTH_PASSWORD", "carbot2026")

    # Sub-configuraciones
    paths: PathConfig = Field(default_factory=PathConfig)
    diagnostic: DiagnosticConfig = Field(default_factory=DiagnosticConfig)

    def validar_seguridad_produccion(self):
        """Valida que no existan secretos predeterminados ni faltantes si el entorno es producción."""
        if self.environment.lower() in ("production", "prod"):
            errores = []
            if not self.meta_app_secret or "change-me" in self.meta_app_secret.lower():
                errores.append("META_APP_SECRET es obligatorio en producción y no puede ser el valor por defecto.")
            if not self.jwt_secret_key or self.jwt_secret_key == "super_secret_carbot_key_ucv_2026_carabayllo":
                errores.append("JWT_SECRET_KEY utiliza el valor predeterminado inseguro.")
            if self.auth_username == "admin" or self.auth_password == "carbot2026":
                errores.append("AUTH_USERNAME y AUTH_PASSWORD utilizan credenciales predeterminadas.")
            if not self.twilio_auth_token:
                errores.append("TWILIO_AUTH_TOKEN no está configurado.")
            if not self.privacy_secret_key or self.privacy_secret_key == "carbot_privacy_hmac_secret_key_2026":
                errores.append("PRIVACY_SECRET_KEY utiliza la clave predeterminada.")

            if errores:
                msg = "Fallo de validación de seguridad en PRODUCCIÓN:\n - " + "\n - ".join(errores)
                raise RuntimeError(msg)


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

    @TWILIO_AUTH_TOKEN.setter
    def TWILIO_AUTH_TOKEN(self, value: str):
        self.twilio_auth_token = value

    @property
    def VERIFY_TOKEN(self) -> str:
        return self.verify_token

    @property
    def META_VERIFY_TOKEN(self) -> str:
        return self.meta_verify_token

    @META_VERIFY_TOKEN.setter
    def META_VERIFY_TOKEN(self, value: str):
        self.meta_verify_token = value

    @property
    def META_APP_SECRET(self) -> str:
        return self.meta_app_secret

    @META_APP_SECRET.setter
    def META_APP_SECRET(self, value: str):
        self.meta_app_secret = value

    @property
    def JWT_SECRET_KEY(self) -> str:
        return self.jwt_secret_key

    @JWT_SECRET_KEY.setter
    def JWT_SECRET_KEY(self, value: str):
        self.jwt_secret_key = value

    @property
    def TOKEN_WHATSAPP(self) -> str:
        return self.token_whatsapp

    @property
    def TELEFONO_ID(self) -> str:
        return self.telefono_id

    @property
    def PRIVACY_SECRET_KEY(self) -> str:
        return self.privacy_secret_key

    @PRIVACY_SECRET_KEY.setter
    def PRIVACY_SECRET_KEY(self, value: str):
        self.privacy_secret_key = value


# Instancia global de configuración centralizada
settings = AppSettings()
