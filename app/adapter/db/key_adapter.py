import logging
from datetime import datetime
from fastapi import HTTPException
from app.db.session_windows import get_jtds_connection
from app.db.models import SecurityKeyRecordCreateModel, SecurityKeyRecord, SecurityKeyRecordFileModel

logger = logging.getLogger(__name__)

class KeyAdapter:
    def __init__(self):
        self.connection = get_itds_connection()

    def get_latest_active_log(self) -> SecurityKeyRecord:
        query = """
        SELECT PrivateKey, PublicKey, IsActive, CreatedBy, CreationDate
        FROM CONECTINTEG.dbo.SecurityKeyRecords
        WHERE IsActive = 1
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(query)
            result = cursor.fetchone()
            
            # Verificar si result no es None
            if result:
                # Definir los nombres de las columnas en el mismo orden que aparecen en el SELECT
                columns = [
                    "PrivateKey", "PublicKey", "IsActive", "CreatedBy", "CreationDate"
                ]
                
                # Convertir la tupla resultante en un diccionario
                result_dict = dict(zip(columns, result))
                
                # Pasar el diccionario al modelo Pydantic
                return SecurityKeyRecord(**result_dict)
            else:
                raise HTTPException(status_code=404, detail="No active log found.")
        except Exception as e:
            logger.error(f"Error al ejecutar la consulta: {e}")
            raise HTTPException(status_code=500, detail="Internal server error.")
        finally:
            cursor.close()
            self.connection.close()

    def get_public_key_file_log(self) -> SecurityKeyRecordFileModel:
        query = """
        SELECT PrivateKey, PublicKey, PrivateKeyFile, PublicKeyFile
        FROM CONECTINTEG.dbo.SecurityKeyRecords
        WHERE IsActive = 1
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(query)
            result = cursor.fetchone()
            
            # Verificar si result no es None
            if result:
                # Definir los nombres de las columnas en el mismo orden que aparecen en el SELECT
                columns = [
                    "PrivateKey", "PublicKey", "PrivateKeyFile", "PublicKeyFile"
                ]
                
                # Convertir la tupla resultante en un diccionario
                result_dict = dict(zip(columns, result))
                
                # Pasar el diccionario al modelo Pydantic
                return SecurityKeyRecordFileModel(**result_dict)
            else:
                raise HTTPException(status_code=404, detail="No active log found.")
        except Exception as e:
            logger.error(f"Error al ejecutar la consulta: {e}")
            raise HTTPException(status_code=500, detail="Internal server error.")
        finally:
            cursor.close()
            self.connection.close()

    def create_security_key_record(self, record: SecurityKeyRecordCreateModel) -> SecurityKeyRecordCreateModel:
        query = """
        INSERT INTO CONECTINTEG.dbo.SecurityKeyRecords (
            PrivateKey, PublicKey, PrivateKeyFile, PublicKeyFile, IsActive, CreatedBy, CreationDate
        ) VALUES (%s, %s, CONVERT(varbinary(max), %s), CONVERT(varbinary(max), %s), %s, %s, %s)
        """
        try:
            connection = get_jtds_connection()
            cursor = connection.cursor()
            
            # Convertir las fechas a cadenas si es necesario, o mantenerlas como datetime si se maneja adecuadamente.
            cursor.execute(query, (
                record.PrivateKey,  # PrivateKey
                record.PublicKey,   # PublicKey
                record.PrivateKeyFile,  # PrivateKeyFile (sin CAST explícito en Python, el controlador debe manejarlo)
                record.PublicKeyFile,   # PublicKeyFile (sin CAST explícito en Python)
                record.IsActive,    # IsActive (bit)
                record.CreatedBy,   # CreatedBy
                record.CreationDate.strftime('%Y-%m-%d %H:%M:%S'),  # CreationDate
            ))
            connection.commit()
        except Exception as e:
            logger.error(f"Error al crear llaves: {e}")
            raise HTTPException(status_code=500, detail="Internal server error.")
        finally:
            cursor.close()
            self.connection.close()

    def deseable_old_security_key_records(self, date: datetime, user: str):
        query = """
        UPDATE CONECTINTEG.dbo.SecurityKeyRecords
        SET IsActive = 0, ModificationDate = %s, ModifiedBy = %s
        WHERE IsActive = %s AND CreationDate < %s
        """
        try:
            connection = get_jtds_connection()
            cursor = connection.cursor()
            
            date_str = date.strftime('%Y-%m-%d %H:%M:%S')
            
            cursor.execute(query, (date_str, user, 1, date_str))
            connection.commit()
        except Exception as e:
            logger.error(f"Error al actualizar los registros: {e}")
            raise HTTPException(status_code=500, detail="Internal server error.")
        finally:
            cursor.close()
            self.connection.close()