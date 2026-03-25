from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class SubtareaCreate(BaseModel):
    titulo: str


class SubtareaResponse(BaseModel):
    id: int
    titulo: str
    completada: bool

    model_config = {"from_attributes": True}


class ProcesoCreate(BaseModel):
    titulo: str
    descripcion: Optional[str] = None
    expediente_id: Optional[int] = None
    usuario_ids: list[int] = []


class ProcesoUpdate(BaseModel):
    titulo: Optional[str] = None
    descripcion: Optional[str] = None
    estado: Optional[str] = None
    expediente_id: Optional[int] = None


class ProcesoResponse(BaseModel):
    id: int
    titulo: str
    descripcion: Optional[str] = None
    estado: str
    expediente_id: Optional[int] = None
    expediente_nombre: Optional[str] = None
    creador_id: int
    usuarios: list[dict] = []
    subtareas: list[SubtareaResponse] = []
    progreso: float = 0.0
    fecha_creacion: Optional[datetime] = None

    model_config = {"from_attributes": True}
