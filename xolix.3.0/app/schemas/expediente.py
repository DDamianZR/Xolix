from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ExpedienteCreate(BaseModel):
    nombre: str
    descripcion: Optional[str] = None


class ExpedienteResponse(BaseModel):
    id: int
    nombre: str
    descripcion: Optional[str] = None
    archivo_path: str
    tipo_archivo: str
    propietario_id: int
    fecha_creacion: Optional[datetime] = None

    model_config = {"from_attributes": True}


class CompartirExpediente(BaseModel):
    correo_destino: str
    permiso: str = "lectura"  # "lectura" o "edicion"


class ExpedienteCompartidoResponse(BaseModel):
    id: int
    expediente_id: int
    usuario_id: int
    permiso: str
    fecha_compartido: Optional[datetime] = None

    model_config = {"from_attributes": True}
