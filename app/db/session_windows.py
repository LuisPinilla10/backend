# Este código configura y valida una conexión a una base de datos SQL Server usando SQLAlchemy y PyODBC. Utiliza variables de entorno
# para definir parámetros como el host, puerto, nombre de la base de datos, usuario y contraseña y tipo de autenticación (integrada o
# con credenciales). Crea un motor de conexión (engine) y una fábrica de sesiones (SessionLocal) para ejecutar consultas. También incluye
# funciones para validar la conexión (compatibilidad con código antiguo. Al ejecutarse directamente, intenta conectarse y muestra el
# nombre de la base de datos si la conexión es exitosa.

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os
import logging
from urllib.parse import quote_plus

logger = logging.getLogger(__name__)

# Variables de entorno (ajusta según necesites)
DB_HOST = os.getenv("DB_HOST", "STMDEBDGHM@3V")
DB_PORT = os.getenv("DB_PORT", "57856")  # puerto por defecto
DB_NAME = os.getenv("DB_NAME", "CONECTINTEG")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_DRIVER = os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server")
# Escapar el driver
escaped_driver = quote_plus(DB_DRIVER)
USE_SSPI = os.getenv("USE_SSPI", "true").lower() == "true"

# Crear el engine SQLAlchemy
def get_sqlalchemy_engine():
    try:
        if USE_SSPI:
            connection_string = (
                f"mssql+pyodbc://@{DB_HOST}:{DB_PORT}/{DB_NAME}?"
                f"?driver={escaped_driver}&trusted_connection=yes"
            )
        else:
            connection_string = (
                f"mssql+pyodbc://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}?"
                f"?driver={escaped_driver}"
            )

        logger.info(f"Creando engine con: {connection_string}")
        engine = create_engine(connection_string, echo=False, future=True)
        return engine
    except Exception as e:
        logger.error(f"Error creando engine de SQLAlchemy: {e}")
        raise

# Crear session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=get_sqlalchemy_engine())

def get_jtds_connection():
    """Compatibilidad con código antiguo que espera esta función."""
    return SessionLocal().connection()

def validate_connection():
    try:
        with SessionLocal() as session:
            result = session.execute(text("SELECT 1")).scalar()
            return f"Conexión exitosa. Resultado: {result}"
    except Exception as e:
        return f"Error de conexión: {e}"

# Validar conexión
if __name__ == "__main__":
    try:
        engine = get_sqlalchemy_engine()
        with engine.connect() as conn:
            result = conn.execute(text("SELECT DB_NAME()"))
            db_name = result.scalar()
            logger.info(f"Conexión exitosa a la base de datos: {db_name}")
            print(f"Conexión exitosa a la base de datos: {db_name}")
    except Exception as e:
        logger.error(f"Error de conexión: {e}")
        print(f"Error de conexión: {e}")