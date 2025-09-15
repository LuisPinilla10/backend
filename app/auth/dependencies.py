# Recibe el token JWT automáticamente desde el encabezado Authorization gracias a Depends(oauth2_scheme).
# Verifica el token usando verify_token(token).
# Si el token es inválido o no contiene el campo "sub" (que normalmente representa el ID o nombre del usuario), lanza un error
# 401 Unauthorized.
# Si el token es válido, retorna el valor de sub, que representa el usuario autenticado.

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.utils.token import verify_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token") # Asegúrate que la ruta sea la correcta

def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = verify_token(token)
    if payload is None or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload["sub"]