# version anterior

# main.py
# CAMBIOS MÍNIMOS: Solo agregar CORS para el frontend Angular

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware  # ← NUEVO: Para CORS
from app.router import keys_router, health_checker_router, user_router
from app.utils.token import create_access_token
from app.auth.dependencies import get_current_user
from ldap3 import Server, Connection, ALL, NTLM

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

# ← NUEVO: Configurar CORS para Angular
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],  # Frontend Angular
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Renewed-Token"]  # ← IMPORTANTE: Para token renovado
)

# Incluir tus routers (SIN CAMBIOS)
app.include_router(keys_router.router, prefix="/api/v1/keys")
app.include_router(user_router.router, prefix="/api/v1/user")
app.include_router(health_checker_router.router, prefix="/api/v1/health")

# Función para validar contra Active Directory (SIN CAMBIOS)
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

# Ruta para obtener el token de autenticación (login local) - SIN CAMBIOS
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

# Ruta protegida de ejemplo - SIN CAMBIOS
@app.get("/api/v1/protected")
def protected_route(current_user: dict = Depends(get_current_user)):
    return {"message": f"Hola, {current_user['sub']}! Tienes acceso al recurso protegido."}

# Ruta para validar con Active Directory - SIN CAMBIOS
@app.post("/ldap")
def login_ldap(form_data: OAuth2PasswordRequestForm = Depends()):
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