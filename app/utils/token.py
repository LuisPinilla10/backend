# Este código implementa la creación y verificación de tokens JWT (JSON Web Tokens) para autenticación en aplicaciones web. Utiliza
# una clave secreta y el algoritmo HS256 para firmar los tokens. La función create_access_token genera un token que incluye los datos
# proporcionados y una fecha de expiración (por defecto, 5 minutos), mientras que verify_token intenta decodificar y validar el token
# recibido; si es válido, devuelve su contenido, y si no, retorna None, lo que indica que el token es inválido o ha expirado.

from datetime import datetime, timedelta
from jose import JWTError, jwt
import logging

logger = logging.getLogger(__name__)

# Clave secreta (reemplázala por algo seguro)
SECRET_KEY = "mi_clave_secreta_super_segura"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 5

def create_access_token(data: dict, expires_delta: timedelta = None):
    logger.info("🎫 Creando nuevo JWT token...")
    logger.info(f"📋 Datos para el token: {data}")

    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})

    logger.info(f"⏰ Token expirará el: {expire}")
    logger.info(f"⏳ Duración del token: {ACCESS_TOKEN_EXPIRE_MINUTES} minutos")

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    logger.info(f"✅ JWT creado exitosamente - Length: {len(encoded_jwt)}")
    logger.info(f"🔑 Token preview: {encoded_jwt[:30]}...")

    return encoded_jwt

def verify_token(token: str):
    logger.info("🔍 Verificando JWT token...")
    logger.info(f"🔑 Token preview: {token[:30]}...")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        logger.info("✅ JWT válido - token decodificado exitosamente")
        logger.info(f"👤 Usuario del token: {payload.get('sub', 'N/A')}")
        logger.info(f"⏰ Token expira: {datetime.fromtimestamp(payload.get('exp', 0))}")
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("⏰ JWT expirado - token ya no es válido")
        return None
    except jwt.InvalidTokenError:
        logger.warning("❌ JWT inválido - token malformado o corrupto")
        return None
    except JWTError as e:
        logger.error(f"💥 Error al verificar JWT: {str(e)}")
        return None