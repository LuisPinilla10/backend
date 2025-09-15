# Este código en FastAPI define un endpoint POST en la ruta /db que sirve para verificar si la conexión a la base de datos está
# funcionando correctamente; al recibir una solicitud, ejecuta la función db_checker() (que realiza la validación), registra el
# proceso en los logs, y devuelve un mensaje con el resultado si todo sale bien, o lanza una excepción HTTP 500 con el detalle
# del error si ocurre algún problema durante la verificación.

from fastapi import APIRouter, HTTPException
from app.logic.db_health_checker_logic import db_checker
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/db")
def health_checker_db():
    """Validar conexión a bd"""
    try:
        logger.info("Starting health check process")
        result = db_checker()
        logger.info("Health check process completed successfully")
        return {"message": result}
    except Exception as e:
        logger.error(f"Health check process failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))