from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from datetime import date, datetime
from app.validators.mexican_ids import validar_rfc, validar_curp


class UserCreate(BaseModel):
    nombre: str
    apellido_paterno: str
    apellido_materno: str
    rfc: str
    curp: str
    sexo: str
    fecha_nacimiento: date
    estado: str
    municipio: str
    colonia: str
    calle: str
    numero: str
    codigo_postal: str
    calles_aledanas: Optional[str] = None
    tipo_personal: str
    rol: str
    correo: EmailStr
    password: str

    @field_validator('rfc')
    @classmethod
    def validate_rfc(cls, v):
        ok, msg = validar_rfc(v)
        if not ok:
            raise ValueError(msg)
        return v.strip().upper()

    @field_validator('curp')
    @classmethod
    def validate_curp(cls, v):
        ok, msg = validar_curp(v)
        if not ok:
            raise ValueError(msg)
        return v.strip().upper()

    @field_validator('sexo')
    @classmethod
    def validate_sexo(cls, v):
        if v.upper() not in ('M', 'F'):
            raise ValueError("Sexo debe ser 'M' o 'F'")
        return v.upper()

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError("La contraseña debe tener al menos 6 caracteres")
        return v


class UserUpdate(BaseModel):
    nombre: Optional[str] = None
    apellido_paterno: Optional[str] = None
    apellido_materno: Optional[str] = None
    rfc: Optional[str] = None
    curp: Optional[str] = None
    sexo: Optional[str] = None
    fecha_nacimiento: Optional[date] = None
    estado: Optional[str] = None
    municipio: Optional[str] = None
    colonia: Optional[str] = None
    calle: Optional[str] = None
    numero: Optional[str] = None
    codigo_postal: Optional[str] = None
    calles_aledanas: Optional[str] = None
    tipo_personal: Optional[str] = None
    rol: Optional[str] = None
    correo: Optional[EmailStr] = None
    password: Optional[str] = None

    @field_validator('rfc')
    @classmethod
    def validate_rfc(cls, v):
        if v is None:
            return v
        ok, msg = validar_rfc(v)
        if not ok:
            raise ValueError(msg)
        return v.strip().upper()

    @field_validator('curp')
    @classmethod
    def validate_curp(cls, v):
        if v is None:
            return v
        ok, msg = validar_curp(v)
        if not ok:
            raise ValueError(msg)
        return v.strip().upper()


class UserLogin(BaseModel):
    correo: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    nombre: str
    apellido_paterno: str
    apellido_materno: str
    rfc: str
    curp: str
    sexo: str
    fecha_nacimiento: date
    edad: int
    estado: str
    municipio: str
    colonia: str
    calle: str
    numero: str
    codigo_postal: str
    calles_aledanas: Optional[str] = None
    tipo_personal: str
    rol: str
    correo: str
    activo: bool
    foto_perfil: Optional[str] = None
    fecha_creacion: Optional[datetime] = None

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    rol: str
