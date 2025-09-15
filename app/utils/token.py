# Este código implementa la creación y verificación de tokens JWT (JSON Web Tokens) para autenticación en aplicaciones web. Utiliza
# una clave secreta y el algoritmo HS256 para firmar los tokens. La función create_access_token genera un token que incluye los datos
# proporcionados y una fecha de expiración (por defecto, 5 minutos), mientras que verify_token intenta decodificar y validar el token
# recibido; si es válido, devuelve su contenido, y si no, retorna None, lo que indica que el token es inválido o ha expirado.

from datetime import datetime, timedelta
from jose import JWTError, jwt

# Clave secreta (reemplázala por algo seguro)
SECRET_KEY = "mi_clave_secreta_super_segura"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 5

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