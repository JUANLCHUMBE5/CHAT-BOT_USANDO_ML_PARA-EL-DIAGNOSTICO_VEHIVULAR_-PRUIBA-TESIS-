from slowapi import Limiter
from slowapi.util import get_remote_address

# Instancia centralizada del Limiter de SlowAPI para evitar importaciones circulares entre main y routers
limiter = Limiter(key_func=get_remote_address, default_limits=["60 per minute"])
