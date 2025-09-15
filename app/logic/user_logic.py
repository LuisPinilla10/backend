# Este código define una serie de funciones para gestionar usuarios en una aplicación, utilizando un adaptador (UserAdapter) que se
# encarga de interactuar con la base de datos. Las funciones permiten crear, modificar, consultar usuarios y asignar roles, todo con
# manejo de errores mediante bloques try-except que registran cualquier fallo. Además, incluye una función de inicio de sesión (login)
# que simula la autenticación de un usuario y genera un token (tipo bearer) usando información básica del usuario, lo cual
# es útil para controlar el acceso a recursos protegidos dentro de la aplicación. En conjunto, el código proporciona una interfaz
# sencilla para operaciones comunes de administración de usuarios.

from app.adapters.user_adapter import UserAdapter
from app.utils.token import create_access_token

adapter = UserAdapter()

def create(user: str, rol: str = None):
    try:
        return adapter.create_user(user)
    except Exception as e:
        logger.error(f"Error crear usuario: {e}")
        return 'Error'

def modify(user: str, full_name: str, email: str, status: int):
    try:
        return adapter.update_user(user, full_name, email, status)
    except Exception as e:
        logger.error(f"Error modificar usuario: {e}")
        return 'Error'

def consult(user: str):
    try:
        return adapter.get_user(user)
    except Exception as e:
        logger.error(f"Error consultar usuario: {e}")
        return 'Error'

def manage_role(rol_id: int, username: str, asigno: int):
    try:
        return adapter.assign_role(rol_id, username, asigno)
    except Exception as e:
        logger.error(f"Error manejando rol: {e}")
        return 'Error'

def login(username: str, password: str):
    # Aquí validarías username y password con la base de datos
    # Por simplicidad, vamos a asumir que pasa
    
    user_data = {
        "sub": username,
        "perfil": "admin",                    # Puedes obtenerlo de la base de datos
        "email": "usuario@dominio.com",
        "full_name": "Juan Pérez"
    }
    
    access_token = create_access_token(user_data)
    return {"access_token": access_token, "token_type": "bearer"}