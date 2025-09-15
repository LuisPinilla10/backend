# Este código define una API utilizando FastAPI que gestiona llaves RSA para una aplicación. Contiene tres rutas: una para generar un
# par de llaves (pública y privada) usando encabezados HTTP (user_app y user_roll_app), otra para consultar los nombres de las llaves
# activas, y una tercera para descargar la llave pública. Cada ruta maneja posibles errores mediante excepciones HTTP, devolviendo
# mensajes claros en caso de fallos. Las funciones principales (generate_rsa_key_pair, get_public_key_name, download_public_key) están
# importadas desde un módulo de lógica (key_logic), lo que permite una separación entre la lógica de negocio y la capa de presentación.

from fastapi import APIRouter, Header, HTTPException
from app.logic.key_logic import generate_rsa_key_pair, get_public_key_name, download_public_key

router = APIRouter()

@router.post("/generate")
def generate_keys(
    user_app: str = Header(...),
    user_roll_app: str = Header(...)
):
    """Genera un par de llaves (pública y privada)"""
    try:
        response = generate_rsa_key_pair(user_app, user_roll_app)
        return {"message": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/get-active/name-file")
def get_name_keys():
    """Consulta nombre de llaves activas"""
    try:
        result = get_public_key_name()
        return {"private_key": result.PrivateKey, "public_key": result.PublicKey}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/get-active/public/download")
def get_download_public_key():
    """Descargar la llave pública"""
    try:
        public_key = download_public_key()
        if public_key:
            return {"public_key": public_key}
        else:
            raise HTTPException(status_code=404, detail="Llave pública no encontrada.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))