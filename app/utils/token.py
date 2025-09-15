
from datetime import datetime, timedelta
from jose import JWTError, jwt

# Clave secreta (reemplázala por algo seguro)
SECRET_KEY = "mi_clave_secreta_super_segura"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 5  # ← CAMBIO: 5 minutos en lugar de 5

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

# ← NUEVO: Funciones para renovación automática
def should_renew_token(payload: dict) -> bool:
    """Verifica si el token necesita renovación (si quedan menos de 2 minutos)"""
    try:
        exp_timestamp = payload.get("exp")
        if not exp_timestamp:
            return False
        
        exp_time = datetime.utcfromtimestamp(exp_timestamp)
        current_time = datetime.utcnow()
        time_remaining = exp_time - current_time
        
        # Renovar si quedan menos de 2 minutos
        return time_remaining.total_seconds() < 120
    except:
        return False

def renew_token(current_payload: dict) -> str:
    """Renueva un token existente"""
    # Limpiar campos de tiempo del payload anterior
    new_data = {key: value for key, value in current_payload.items() 
               if key not in ["exp", "iat"]}
    
    # Crear nuevo token
    return create_access_token(new_data)