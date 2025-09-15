# Este módulo se encarga de generar, cifrar, almacenar y recuperar llaves RSA (usadas para seguridad y cifrado de datos) de forma segura.
# Utiliza dos tipos de cifrado:
#
# RSA (asimétrico): para generar las llaves pública y privada.
# AES (simétrico): para cifrar esas llaves antes de guardarlas.
#
#
# key_service.py
from fastapi import HTTPException
from app.utils.generate_rsa import RSAKeyGenerator
from app.utils.encrypt_data import AESCipher
from app.adapter.db.key_adapter import KeyAdapter
from app.db.models import SecurityKeyRecordCreateModel
import uuid
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def generate_rsa_key_pair(user: str, rol: str):
    try:
        
        """PASO: Genera un par de llaves RSA (pública y privada)"""
        key_gen = RSAKeyGenerator()
        private_asc, public_asc = key_gen.generate_keys()
        
        print(private_asc)
        print(public_asc)
        
        """PASO: cifrar data"""
        aes = AESCipher()
        private_asc_aes = aes.encrypt(private_asc)
        public_asc_aes = aes.encrypt(public_asc)
        
        """PASO: generar nombre"""
        name_uuid_key = uuid.uuid4()
        private_key_name = "CPR_" + str(name_uuid_key) + ".asc"
        public_key_name = "CPU_" + str(name_uuid_key) + ".asc"
        
        """PASO: guardar en bd"""
        date = datetime.now()
        security_key_record = SecurityKeyRecordCreateModel(
            PrivateKey=private_key_name,
            PublicKey=public_key_name,
            PrivateKeyFile=private_asc_aes,
            PublicKeyFile=public_asc_aes,
            IsActive=1,
            CreatedBy=str(user),
            CreationDate=date
        )
        
        key_adapter = KeyAdapter()
        key_adapter.create_security_key_record(security_key_record)
        
        """PASO: actualización de registros antiguos de llaves de seguridad"""
        key_adapter.deseable_old_security_key_records(date, str(user))
        
        return 'Success'
    except Exception as e:
        logger.error(f"Error crear key: {e}")
        return 'Error'

def get_public_key_name():
    key_adapter = KeyAdapter()
    return key_adapter.get_latest_active_log()

def download_public_key():
    try:
        key_adapter = KeyAdapter()
        keys_data = key_adapter.get_public_key_file_log()
        
        key_gen = AESCipher()
        keyPublic = key_gen.decrypt(keys_data.PublicKeyFile.decode('utf-8'))
        #keyPrivate = key_gen.decrypt(keys_data.PrivateKeyFile.decode('utf-8'))
        
        with open(keys_data.PublicKey, 'w', encoding='utf-8') as file:
            file.write(keyPublic)
            
        #with open(keys_data.PrivateKey, 'w', encoding='utf-8') as file:
        #    file.write(keyPrivate)
        
        return 'Success'
    except Exception as e:
        logger.error(f"Error download key: {e}")
        return 'Error'