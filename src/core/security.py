import hmac
import hashlib
import time
import jwt
from typing import Optional, Dict, Any
from fastapi import HTTPException, Security, status, Header, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from src.config import settings

# HTTP Bearer scheme for Swagger UI & API protection
security_bearer = HTTPBearer(auto_error=False)

# Configuración JWT por defecto (2 horas de expiración = 120 minutos)
JWT_SECRET_KEY = getattr(settings, "JWT_SECRET_KEY", "super_secret_carbot_key_ucv_2026_carabayllo")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_SECONDS = 2 * 60 * 60  # 2 horas = 7200 segundos

def _obtener_jwt_secret() -> str:
    return getattr(settings, "JWT_SECRET_KEY", "super_secret_carbot_key_ucv_2026_carabayllo")

def crear_jwt_token(sub: str = "taller_mecanico", extra_claims: Optional[Dict[str, Any]] = None) -> str:
    """
    Genera un token JWT firmado digitalmente con validez exacta de 2 HORAS.
    """
    ahora = int(time.time())
    payload = {
        "sub": sub,
        "iat": ahora,
        "exp": ahora + JWT_EXPIRATION_SECONDS,
        "iss": "CarBot-API-V1"
    }
    if extra_claims:
        payload.update(extra_claims)
        
    token = jwt.encode(payload, _obtener_jwt_secret(), algorithm=JWT_ALGORITHM)
    return token

def verificar_jwt_token(credentials: Optional[HTTPAuthorizationCredentials] = Security(security_bearer)) -> Dict[str, Any]:
    """
    Middleware / Dependencia para verificar la validez y expiración del Token JWT.
    Lanza HTTP 401 Unauthorized si el token no existe, expiró o fue alterado.
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Falta el encabezado de autorización (Authorization: Bearer <token>).",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    try:
        payload = jwt.decode(token, _obtener_jwt_secret(), algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="El token JWT ha expirado (validez máxima de 2 horas). Por favor genere uno nuevo en /api/v1/auth/login.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token JWT inválido o firma alterada.",
            headers={"WWW-Authenticate": "Bearer"},
        )

def verificar_firma_meta(raw_body: bytes, signature_header: Optional[str]) -> bool:
    """
    Valida la firma criptográfica X-Hub-Signature-256 proveniente de Meta Cloud API (WhatsApp).
    Falla CERRADO (devuelve False) si el secreto de la app o el encabezado de firma no existen.
    """
    app_secret = getattr(settings, "META_APP_SECRET", "")
    if not app_secret:
        # Modo estricto / Falla cerrado: No permitir sin secreto configurado
        return False
        
    if not signature_header or not signature_header.startswith("sha256="):
        return False
        
    expected_sig = signature_header.split("sha256=")[1]
    calculated_sig = hmac.new(
        app_secret.encode('utf-8'),
        raw_body,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(expected_sig, calculated_sig)

def verificar_firma_twilio(url: str, params: Dict[str, Any], signature_header: Optional[str]) -> bool:
    """
    Valida la firma criptográfica X-Twilio-Signature enviada por solicitudes de Twilio.
    Algoritmo: HMAC-SHA1 codificado en Base64 sobre la URL + parámetros POST ordenados alfabéticamente.
    """
    auth_token = getattr(settings, "TWILIO_AUTH_TOKEN", "")
    if not auth_token or not signature_header:
        return False

    import base64
    # Construir cadena de firma: URL + claves y valores ordenados por clave
    s = url
    for key in sorted(params.keys()):
        # Si la lista tiene múltiples valores, tomar el primero o concatenar
        val = params[key]
        val_str = val[0] if isinstance(val, list) else str(val)
        s += f"{key}{val_str}"

    mac = hmac.new(auth_token.encode('utf-8'), s.encode('utf-8'), hashlib.sha1)
    calculated_sig = base64.b64encode(mac.digest()).decode('utf-8').strip()

    return hmac.compare_digest(calculated_sig, signature_header.strip())

def anonimizar_identificador(identificador: str) -> str:
    """
    Pseudonimiza de forma segura placas o números telefónicos usando HMAC-SHA256 con sal/secreto de privacidad.
    Protege la privacidad (GDPR / LDP) impidiendo ataques por fuerza bruta o listas precalculadas.
    Ejemplo: 'ABC-123' -> 'PLACA_a8f9c10b12c3' | '51987654321' -> 'TEL_3f7b19a08e1d'
    """
    if not identificador or identificador in ("SIN-PLACA", "DESCONOCIDO", "REST-API", "WAPP-01"):
        return identificador
        
    val_limpio = identificador.strip()
    secret = getattr(settings, "PRIVACY_SECRET_KEY", "carbot_privacy_hmac_secret_key_2026")
    
    h = hmac.new(
        secret.encode('utf-8'),
        val_limpio.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()[:12]

    if val_limpio.isdigit() or val_limpio.startswith("whatsapp:") or val_limpio.startswith("+"):
        prefix = "TEL_"
    elif val_limpio.startswith("sess") or val_limpio.startswith("SESS"):
        prefix = "SESS_"
    else:
        prefix = "PLACA_"
        
    return f"{prefix}{h}"

