# Este código define modelos de datos con Pydantic para gestionar llaves de seguridad RSA y usuarios en una aplicación,
# permitiendo validar, estructurar y auditar información como claves públicas/privadas, archivos asociados, y datos de
# usuarios (creación, actualización, desactivación), todo con control de quién y cuándo se realizaron los cambios.

from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class KeyLog(BaseModel):
    LlaveRsaId: int
    LlavePrivada: str
    LlavePublica: str
    Activo: bool
    UsuarioCreo: str
    FechaCreacion: str
    UsuarioModifico: str
    FechaModifico: str

class SecurityKeyRecordCreateModel(BaseModel):
    RsaKeyId: Optional[int] = None  # IDENTITY column, usually auto-generated
    PrivateKey: str
    PublicKey: str
    PrivateKeyFile: str
    PublicKeyFile: str
    IsActive: bool
    CreatedBy: str
    CreationDate: datetime
    ModifiedBy: Optional[str] = None
    ModificationDate: Optional[datetime] = None

class SecurityKeyRecord(BaseModel):
    PrivateKey: str
    PublicKey: str
    IsActive: bool
    CreatedBy: str
    CreationDate: datetime

class SecurityKeyRecordFileModel(BaseModel):
    PrivateKey: str
    PublicKey: str
    PrivateKeyFile: bytes
    PublicKeyFile: bytes

class User(BaseModel):
    id: str

class UserLookup(BaseModel):
    username: str

class UserCreate(BaseModel):
    username: str
    full_name: str
    email: str

class UserUpdate(BaseModel):
    username: str
    full_name: str
    email: str
    status: int

class UserDisable(BaseModel):
    username: str
    status: int