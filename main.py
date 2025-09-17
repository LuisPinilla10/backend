# Este código define una aplicación web con FastAPI que gestiona autenticación de usuarios tanto localmente como mediante Active Directory
# (LDAP). Contiene el registro de logs, incluye rutas organizadas en módulos (keys_router, user_router, health_checker_router). 
# establece un ciclo de vida para registrar eventos de inicio y cierre de la app. Proporciona una ruta /token para generar un JWT tras
# autenticación local, y otra /ldap para validar credenciales contra un servidor LDAP corporativo, retornando también un token si el
# usuario es válido. Además, incluye una ruta protegida que requiere autenticación previa (/api/v1/protected) y una función
# validate_user_ad que conecta al servidor LDAP, busca el usuario, verifica si está activo y extrae sus datos como nombre y correo.

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from app.router import keys_router, health_checker_router, user_router
from app.utils.token import create_access_token
from app.auth.dependencies import get_current_user
from ldap3 import Server, Connection, ALL, NTLM
import requests
import json

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(asctime)s - %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application startup")
    yield
    logger.info("Application shutdown")

app = FastAPI(lifespan=lifespan)

# Configurar CORS para permitir conexiones desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir tus routers
app.include_router(keys_router.router, prefix="/api/v1/keys")
app.include_router(user_router.router, prefix="/api/v1/user")
app.include_router(health_checker_router.router, prefix="/api/v1/health")

# Función para validar token MSAL contra Microsoft Graph
def validate_msal_token(access_token: str):
    logger.info("🔍 Iniciando validación del token MSAL contra Microsoft Graph")

    try:
        # Validar token contra Microsoft Graph API
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        logger.info("📡 Enviando petición a Microsoft Graph API...")

        # Obtener información del usuario desde Microsoft Graph
        response = requests.get('https://graph.microsoft.com/v1.0/me', headers=headers, timeout=10)

        logger.info(f"📨 Respuesta de Microsoft Graph: Status {response.status_code}")

        if response.status_code != 200:
            logger.warning(f"❌ Token MSAL inválido: Status {response.status_code}")
            logger.warning(f"Response body: {response.text[:200]}...")
            return False

        user_data = response.json()
        logger.info(f"✅ Usuario MSAL validado exitosamente: {user_data.get('userPrincipalName')}")
        logger.info(f"👤 Datos del usuario: nombre={user_data.get('displayName')}, email={user_data.get('mail')}")

        result = {
            "username": user_data.get('userPrincipalName', ''),
            "full_name": user_data.get('displayName', ''),
            "email": user_data.get('mail', user_data.get('userPrincipalName', '')),
            "user_id": user_data.get('id', '')
        }

        logger.info(f"📋 Datos extraídos para el usuario: {result}")
        return result

    except requests.exceptions.Timeout:
        logger.error("⏰ Timeout al conectar con Microsoft Graph API")
        return False
    except requests.exceptions.ConnectionError:
        logger.error("🚫 Error de conexión con Microsoft Graph API")
        return False
    except Exception as e:
        logger.error(f"💥 Error inesperado al validar token MSAL: {str(e)}")
        logger.error(f"Tipo de error: {type(e).__name__}")
        return False

# Función para validar contra Active Directory
def validate_user_ad(username: str, password: str):
    ad_server = 'Bancolombia.corp'  # Servidor LDAP
    ad_base_dn = 'OU=Banistmo,OU=Usuarios,DC=BANCOLOMBIA,DC=CORP'  # DN base correcto
    user_dn = f"juanv@bancolombia.corp"  # o f"CN={username},{ad_base_dn}" si sabes que CN es el username
    password = "erh0Bg100632042G"

    try:
        server = Server(ad_server, get_info=ALL)
        conn = Connection(server, user=user_dn, password=password, auto_bind=True)
        search_filter = f"(&(sAMAccountName={username}))"
        conn.search(ad_base_dn, search_filter, attributes=['userAccountControl', 'displayName', 'mail'])
        
        if not conn.entries:
            logger.warning(f"Usuario {username} no encontrado en AD.")
            return False
        
        entry = conn.entries[0]
        user_account_control = int(entry.userAccountControl.value)
        if user_account_control & 2:
            logger.warning(f"Usuario {username} está deshabilitado en AD.")
            return False
        
        logger.info(f"Usuario {username} válido en AD: {entry.displayName.value}, {entry.mail.value}")
        return {
            "username": username,
            "full_name": entry.displayName.value,
            "email": entry.mail.value
        }
    
    except Exception as e:
        logger.error(f"Error al validar usuario {username} contra AD: {e}")
        return False

# Ruta para obtener el token de autenticación (login local)
@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    username = form_data.username
    user_data = {
        "sub": username,
        "perfil": "admin",  # Puedes obtenerlo de la base de datos
        "email": "usuario@dominio.com",
        "full_name": "Juan Pérez"
    }
    token = create_access_token(user_data)
    return {"access_token": token, "expires": "bearer", "status": "bearer", "token_type": "bearer"}

# Ruta protegida de ejemplo
@app.get("/api/v1/protected")
def protected_route(current_user: dict = Depends(get_current_user)):
    return {"message": f"Hola, {current_user['sub']}! Tienes acceso al recurso protegido."}

# Ruta para validar con MSAL o Active Directory
@app.post("/msal")
def login_msal(form_data: OAuth2PasswordRequestForm = Depends()):
    logger.info("=== NUEVA PETICIÓN AL ENDPOINT /msal ===")
    logger.info(f"Username recibido: {form_data.username}")
    logger.info(f"Password length: {len(form_data.password) if form_data.password else 0}")

    # Si username es "msal_token", el password contiene el access token de MSAL
    if form_data.username == "msal_token":
        access_token = form_data.password
        logger.info("🔑 Detectado token MSAL - iniciando validación")
        logger.info(f"Token preview: {access_token[:50]}..." if len(access_token) > 50 else f"Token: {access_token}")

        user_info = validate_msal_token(access_token)
        if not user_info:
            logger.error("❌ Token MSAL inválido - rechazando petición")
            raise HTTPException(status_code=401, detail="Token MSAL inválido o expirado.")

        logger.info("✅ Token MSAL válido - creando JWT interno")
        user_data = {
            "sub": user_info["username"],
            "perfil": "empleado",  # Puedes personalizar según el rol real
            "email": user_info["email"],
            "full_name": user_info["full_name"],
            "user_id": user_info["user_id"]
        }
        logger.info(f"User data para JWT: {user_data}")

        token = create_access_token(user_data)
        logger.info(f"🎫 JWT creado exitosamente - expira en 5 minutos")
        logger.info(f"JWT preview: {token[:50]}...")
        return {"access_token": token, "token_type": "bearer"}

    # Fallback a validación LDAP tradicional
    else:
        username = form_data.username
        password = form_data.password

        user_info = validate_user_ad(username, password)
        if not user_info:
            raise HTTPException(status_code=401, detail="Credenciales inválidas o usuario no válido en Active Directory.")

        user_data = {
            "sub": username,
            "perfil": "empleado",  # Puedes personalizar según el rol real
            "email": user_info["email"],
            "full_name": user_info["full_name"]
        }

        token = create_access_token(user_data)
        return {"access_token": token, "token_type": "bearer"}