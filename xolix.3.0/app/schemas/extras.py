from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime

class AuditLogResponse(BaseModel):
    id: int
    usuario_id: Optional[int]
    accion: str
    entidad: str
    entidad_id: Optional[int]
    detalles: Optional[Any]
    fecha: datetime

    model_config = {"from_attributes": True}

class ComentarioCreate(BaseModel):
    texto: str

class ComentarioResponse(BaseModel):
    id: int
    proceso_id: int
    usuario_id: int
    texto: str
    fecha: datetime
    usuario_nombre: Optional[str] = None

    model_config = {"from_attributes": True}

class NotificacionResponse(BaseModel):
    id: int
    usuario_id: int
    mensaje: str
    tipo: str
    leida: bool
    fecha: datetime

    model_config = {"from_attributes": True}
