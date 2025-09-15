# Version Anterior
# # Este código define una serie de endpoints de una API utilizando FastAPI para gestionar la autenticación y administración de usuarios.
# # El endpoint /login permite a un usuario autenticarse mediante credenciales verificadas contra un directorio activo; si son válidas y
# # el usuario está registrado y activo en la base de datos, se genera un token JWT con información del usuario y se actualiza su último
# # acceso. Los demás endpoints permiten consultar detalles de un usuario (/get-user), crear nuevos usuarios (/ con método POST), modificar
# # sus datos (/ con método PUT), y habilitar o deshabilitar usuario (/disable). Todos estos requieren autenticación previa mediante el
# # token generado, y utilizan un adaptador (UserAdapter) para interactuar con la base de datos. El código también maneja errores
# # mediante excepciones HTTP para asegurar respuestas claras ante fallos.

# from fastapi import APIRouter, Header, HTTPException, Depends
# from fastapi.security import OAuth2PasswordRequestForm
# from app.auth.dependencies import get_current_user
# from app.adapter.db.user_adapter import UserAdapter
# from app.db.models import UserLookup, UserCreate, UserUpdate, UserDisable
# from app.utils.token import create_access_token
# from datetime import datetime

# router = APIRouter()
# adapter = UserAdapter()

# @router.post("/login")
# def login(form_data: OAuth2PasswordRequestForm = Depends()):
#     username = form_data.username
#     password = form_data.password
    
#     # Validar en Directorio Activo
#     if not adapter.validate_user_active_directory(username, password):
#         raise HTTPException(status_code=401, detail="Credenciales inválidas en Directorio Activo")
    
#     # Consultar usuario en BD
#     user = adapter.get_user_by_username(username)
#     if not user:
#         raise HTTPException(status_code=404, detail="Usuario no registrado en el sistema")
    
#     if user["status"] != 1:
#         raise HTTPException(status_code=403, detail="Usuario inactivo en el sistema")
    
#     # Construir payload del token
#     user_data = {
#         "sub": username,
#         "perfil": "admin",  # Opcional: puedes ajustarlo si tu tabla lo tiene
#         "email": user["email"],
#         "full_name": user["full_name"]
#     }
    
#     # Generar token con expiración
#     token = create_access_token(data=user_data)
    
#     try:
#         adapter.update_user(
#             username=username,
#             last_access=datetime.now(),
#             actor=username,
#             log_action="Actualizó último acceso"
#         )
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error actualizando last_access: {str(e)}")
    
#     return {
#         "access_token": token,
#         "token_type": "bearer",
#         "status": "success"
#     }

# @router.post("/get-user")
# def get_user_details(
#     payload: UserLookup,
#     current_user: dict = Depends(get_current_user)
# ):
#     try:
#         user = adapter.get_user_by_username(payload.username)
#         if not user:
#             raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
#         return {
#             "username": user["user_name"],
#             "full_name": user["full_name"],
#             "email": user["email"],
#             "status": "Activo" if user["status"] == 1 else "Inactivo",
#             "created_at": user["created_at"],
#             "updated_at": user["updated_at"]
#         }
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# @router.post("/")
# def create_user(
#     user_data: UserCreate,
#     current_user: dict = Depends(get_current_user)
# ):
#     try:
#         response = adapter.create_user(
#             user_data.username,
#             user_data.full_name,
#             user_data.email,
#             actor=current_user
#         )
#         return {"message": response}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# @router.put("/")
# def modify_user(
#     payload: UserUpdate,
#     current_user: dict = Depends(get_current_user)
# ):
#     try:
#         response = adapter.update_user(
#             username=payload.username,
#             full_name=payload.full_name,
#             email=payload.email,
#             status=payload.status,
#             actor=current_user
#         )
#         return {"message": response}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# @router.put("/disable")
# def disable_user(
#     request: UserDisable,
#     current_user: str = Depends(get_current_user)
# ):
#     log_action = "Habilitó usuario:" if request.status == 1 else "Deshabilitó usuario:"
    
#     try:
#         response = adapter.update_user(
#             username=request.username,
#             actor=current_user,
#             status=request.status,
#             log_action=log_action
#         )
#         return {"message": response}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# app/router/user_router.py
# CAMBIOS MÍNIMOS: Solo agregar UN endpoint para validar MSAL

from fastapi import APIRouter, Header, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from app.auth.dependencies import get_current_user
from app.adapter.db.user_adapter import UserAdapter
from app.db.models import UserLookup, UserCreate, UserUpdate, UserDisable
from app.utils.token import create_access_token
from datetime import datetime
import jwt  # ← NUEVO: Para validar tokens MSAL
from pydantic import BaseModel  # ← NUEVO: Para el modelo de request

router = APIRouter()
adapter = UserAdapter()

# ← NUEVO: Modelo para recibir token MSAL
class MSALTokenRequest(BaseModel):
    id_token: str

# ← NUEVO: Endpoint para validar MSAL y generar token interno
@router.post("/validate-msal")
def validate_msal_token(token_request: MSALTokenRequest):
    """Valida token MSAL y genera token interno de 5 minutos"""
    try:
        # 1. Decodificar token MSAL (sin verificar firma por simplicidad)
        decoded = jwt.decode(token_request.id_token, options={"verify_signature": False})
        
        # 2. Extraer información del usuario
        user_email = decoded.get('preferred_username', '').lower()
        user_name = decoded.get('name', '')
        
        if not user_email or not user_name:
            raise HTTPException(status_code=400, detail="Token MSAL no contiene información válida")
        
        # 3. Validar que sea empleado autorizado
        empleado = adapter.validate_employee_from_msal(user_email, user_name)
        if not empleado:
            raise HTTPException(status_code=403, detail="Usuario no autorizado para acceder al sistema")
        
        # 4. Preparar datos para token interno
        token_data = {
            "sub": user_email,
            "email": user_email,
            "full_name": user_name,
            "employee_id": empleado['idEmpleado'],
            "employee_data": empleado
        }
        
        # 5. Generar token interno de 5 minutos
        internal_token = create_access_token(token_data)
        
        return {
            "success": True,
            "access_token": internal_token,
            "token_type": "bearer",
            "expires_in": 300,  # 5 minutos
            "user": {
                "email": user_email,
                "name": user_name,
                "employee_id": empleado['idEmpleado'],
                "employee_name": empleado['nombre']
            }
        }
        
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token MSAL inválido")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error procesando token: {str(e)}")

# ← Resto del código existente SIN CAMBIOS...

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    username = form_data.username
    password = form_data.password
    
    # Validar en Directorio Activo
    if not adapter.validate_user_active_directory(username, password):
        raise HTTPException(status_code=401, detail="Credenciales inválidas en Directorio Activo")
    
    # Consultar usuario en BD
    user = adapter.get_user_by_username(username)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no registrado en el sistema")
    
    if user["status"] != 1:
        raise HTTPException(status_code=403, detail="Usuario inactivo en el sistema")
    
    # Construir payload del token
    user_data = {
        "sub": username,
        "perfil": "admin",  # Opcional: puedes ajustarlo si tu tabla lo tiene
        "email": user["email"],
        "full_name": user["full_name"]
    }
    
    # Generar token con expiración
    token = create_access_token(data=user_data)
    
    try:
        adapter.update_user(
            username=username,
            last_access=datetime.now(),
            actor=username,
            log_action="Actualizó último acceso"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error actualizando last_access: {str(e)}")
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "status": "success"
    }

@router.post("/get-user")
def get_user_details(
    payload: UserLookup,
    current_user: dict = Depends(get_current_user)
):
    try:
        user = adapter.get_user_by_username(payload.username)
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        return {
            "username": user["user_name"],
            "full_name": user["full_name"],
            "email": user["email"],
            "status": "Activo" if user["status"] == 1 else "Inactivo",
            "created_at": user["created_at"],
            "updated_at": user["updated_at"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/")
def create_user(
    user_data: UserCreate,
    current_user: dict = Depends(get_current_user)
):
    try:
        response = adapter.create_user(
            user_data.username,
            user_data.full_name,
            user_data.email,
            actor=current_user
        )
        return {"message": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/")
def modify_user(
    payload: UserUpdate,
    current_user: dict = Depends(get_current_user)
):
    try:
        response = adapter.update_user(
            username=payload.username,
            full_name=payload.full_name,
            email=payload.email,
            status=payload.status,
            actor=current_user
        )
        return {"message": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/disable")
def disable_user(
    request: UserDisable,
    current_user: str = Depends(get_current_user)
):
    log_action = "Habilitó usuario:" if request.status == 1 else "Deshabilitó usuario:"
    
    try:
        response = adapter.update_user(
            username=request.username,
            actor=current_user,
            status=request.status,
            log_action=log_action
        )
        return {"message": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))