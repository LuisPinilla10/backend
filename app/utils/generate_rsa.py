# Este código define una clase llamada RSAKeyGenerator que genera un par de llaves PGP (Pretty Good Privacy) –una pública y una
# privada– utilizando el algoritmo RSA de 2048 bits. Al crear la llave, se le asocia un identificador de usuario (PGPUID) con el
# nombre "enlace" y se configuran sus usos (firmar, cifrar comunicaciones y almacenamiento), junto con algoritmos de
# cifrado simétrico (AES256) y compresión (ZLIB). Luego, la llave privada se protege con una frase de contraseña ("enlace") usando
# AES256 y SHA256. Finalmente, el método generate_keys devuelve ambas llaves en formato ASCII-armored (texto plano legible), listas
# para ser utilizadas o almacenadas.

from pgpy.constants import PubKeyAlgorithm, KeyFlags, HashAlgorithm, SymmetricKeyAlgorithm, CompressionAlgorithm
import pgpy

class RSAKeyGenerator:

    def generate_keys(self):
        """Genera un par de llaves PGP (pública y privada) en formato ASC con passphrase"""
        key = pgpy.PGPKey.new(PubKeyAlgorithm.RSAEncryptOrSign, 2048)
        uid = pgpy.PGPUID.new('enlace')
        key.add_uid(uid, usage={KeyFlags.Sign, KeyFlags.EncryptCommunications, KeyFlags.EncryptStorage},
                    hashes=[HashAlgorithm.SHA256],
                    ciphers=[SymmetricKeyAlgorithm.AES256],
                    compression=[CompressionAlgorithm.ZLIB])
        
        # Proteger la llave privada con un passphrase
        key.protect('enlace', SymmetricKeyAlgorithm.AES256, HashAlgorithm.SHA256)
        
        private_asc = str(key)
        public_asc = str(key.pubkey)
        
        return private_asc, public_asc