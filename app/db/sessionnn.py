# Este código en Python está diseñado para establecer y validar una conexión a una base
# driver JTDS a través de la librería Jaydebeapi, que permite conectar Java con bases

import os
import jaydebeapi
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

# Cargar las variables de entorno
load_dotenv()

# Leer las variables de entorno
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_DOMAIN = os.getenv("DB_DOMAIN", None)  # Opcional, si usas un dominio
DB_SSL = os.getenv("DB_SSL", "false")     # Ejemplo de SSL, si es requerido

# Ruta al archivo .jar de JTDS, ubicada en la raíz del proyecto
JTDS_JAR_PATH = os.getenv("JTDS_JAR_PATH", os.path.join(os.getcwd(), "jtds-1.3.1.jar"))

# Formar la cadena de conexión usando JTDS
DATABASE_URL = f"jdbc:jtds:sqlserver://{DB_HOST}:{DB_PORT}/{DB_NAME}"

def get_jtds_connection():
    try:
        # Propiedades de la conexión
        connection_properties = {
            "user": DB_USER,
            "password": DB_PASSWORD,
            "useNTLMv2": "true" if DB_DOMAIN else "false",  # Si usas autenticación NTLM
        }
        
        if DB_DOMAIN:
            connection_properties["domain"] = DB_DOMAIN
        if DB_SSL.lower() == "true":
            connection_properties["ssl"] = "require"
        
        # Conectar usando Jaydebeapi y JTDS
        connection = jaydebeapi.connect(
            "net.sourceforge.jtds.jdbc.Driver",
            DATABASE_URL,
            connection_properties,
            JTDS_JAR_PATH
        )
        logger.info("Conexión exitosa usando JTDS")
        return connection
    except Exception as e:
        logger.error(f"Error de conexión: {e}")
        raise

def validate_connection():
    """Valida la conexión a la base de datos"""
    try:
        # Obtener la conexión
        connection = get_jtds_connection()
        cursor = connection.cursor()
        
        # Ejecutar una consulta de prueba
        cursor.execute("SELECT 1")
        res = cursor.fetchall()
        
        if res:
            logger.info(f"Conexión exitosa. Resultado: {res}")
        
        cursor.close()
        connection.close()
        return "Conexión exitosa, Conexión cerrada correctamente"
    except Exception as e:
        logger.error(f"Error de conexión: {e}")
        return f"Error de conexión: {e}"

# Llamar a la función de validación
if __name__ == "__main__":
    logger.info(validate_connection())