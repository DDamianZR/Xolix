from pydantic import BaseModel

class UserCreate(BaseModel):
    nombre_completo: str
    rfc: str
    curp: str
    sexo: str
    edad: int
    direccion: str
    tipo_personal: str
    rol: str
    correo: str
    password: str


class UserLogin(BaseModel):
    correo: str
    password: str
