from pydantic import BaseModel
from typing import Optional
from datetime import date

class UserCreate(BaseModel):
    nombre_completo: str
    rfc: str
    curp: str
    sexo: str
    fecha_nacimiento: date
    direccion: str
    tipo_personal: str
    rol: str
    correo: str
    password: str

class UserUpdate(BaseModel):
    nombre_completo: Optional[str] = None
    rfc: Optional[str] = None
    curp: Optional[str] = None
    sexo: Optional[str] = None
    fecha_nacimiento: Optional[date] = None
    direccion: Optional[str] = None
    tipo_personal: Optional[str] = None
    rol: Optional[str] = None
    correo: Optional[str] = None
    password: Optional[str] = None

class UserLogin(BaseModel):
    correo: str
    password: str