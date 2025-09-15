# Este código define una clase llamada AESCipher que permite cifrar y descifrar textos utilizando el algoritmo AES en modo CBC.
# Primero, carga una clave secreta desde un archivo .env usando dotenv, y configura el entorno de cifrado con la biblioteca
# cryptography. Al cifrar, genera un vector de inicialización (IV) aleatorio, aplica padding al texto plano, lo cifra y luego
# codifica el resultado en base64. Al descifrar, decodifica el texto cifrado, extrae el IV del contenido y elimina el
# padding para recuperar el texto original. Además, utiliza logging para registrar eventos importantes o errores durante el proceso.

import os
from dotenv import load_dotenv
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
import logging
import base64

# Configurar el logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

class AESCipher:
    def __init__(self):
        try:
            self.key = os.getenv('AES_KEY').encode()  # Obtener la clave desde la variable de entorno
            self.backend = default_backend()
            logger.info("AESCipher initialized successfully.")
        except Exception as e:
            logger.error(f"Error initializing AESCipher: {e}")
            raise

    def encrypt(self, plaintext: str) -> str:
        try:
            iv = os.urandom(16)
            padder = padding.PKCS7(128).padder()
            padded_data = padder.update(plaintext.encode('utf-8')) + padder.finalize()
            cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv), backend=self.backend)
            encryptor = cipher.encryptor()
            encrypted_data = iv + encryptor.update(padded_data) + encryptor.finalize()
            encoded_data = base64.b64encode(encrypted_data).decode('utf-8')
            logger.info("Data encrypted successfully.")
            return encoded_data
        except Exception as e:
            logger.error(f"Error encrypting data: {e}")
            return None

    def decrypt(self, encoded_ciphertext: str) -> str:
        try:
            ciphertext = base64.b64decode(encoded_ciphertext.encode('utf-8'))
            iv = ciphertext[:16]
            cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv), backend=self.backend)
            decryptor = cipher.decryptor()
            padded_data = decryptor.update(ciphertext[16:]) + decryptor.finalize()
            unpadder = padding.PKCS7(128).unpadder()
            decrypted_data = unpadder.update(padded_data) + unpadder.finalize()
            logger.info("Data decrypted successfully.")
            return decrypted_data.decode('utf-8')
        except Exception as e:
            logger.error(f"Error decrypting data: {e}")
            return None