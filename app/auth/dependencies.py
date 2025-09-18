
from fastapi import Depends, HTTPException, status, Response
from fastapi.security import OAuth2PasswordBearer
from app.utils.token import verify_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token") # Asegúrate que la ruta sea la correcta

# ← MODIFICADO: Agregar Response para enviar token renovado
def get_current_user(response: Response, token: str = Depends(oauth2_scheme)):
    payload = verify_token(token)
    if payload is None or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return payload["sub"]