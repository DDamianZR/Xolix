from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, date


class MiembroBase(BaseModel):
    usuario_id: int
    rol_en_equipo: str
    observaciones: Optional[str] = None


class MiembroCreate(MiembroBase):
    pass


class MiembroUpdate(BaseModel):
    rol_en_equipo: str


class UsuarioResumen(BaseModel):
    id: int
    nombre: str
    apellido_paterno: str
    correo: str
    rol: str
    tipo_colaboracion: Optional[str] = "planta"
    nivel_confianza: Optional[int] = 3

    model_config = {"from_attributes": True}


class MiembroResponse(BaseModel):
    id: int
    caso_id: int
    usuario_id: int
    rol_en_equipo: str
    fecha_asignacion: datetime
    activo: bool
    observaciones: Optional[str] = None
    usuario: Optional[UsuarioResumen] = None

    model_config = {"from_attributes": True}


class AsignarResponsableRequest(BaseModel):
    responsable_id: int


class EvaluacionCreate(BaseModel):
    nivel_nuevo: int = Field(..., ge=1, le=5)
    justificacion: str = Field(..., min_length=10)


class EvaluacionResponse(BaseModel):
    id: int
    usuario_id: int
    evaluador_id: int
    nivel_anterior: int
    nivel_nuevo: int
    justificacion: str
    fecha: datetime
    evaluador: Optional[UsuarioResumen] = None

    model_config = {"from_attributes": True}


class ColaboradorResponse(BaseModel):
    id: int
    nombre: str
    apellido_paterno: str
    apellido_materno: str
    correo: str
    rol: str
    tipo_colaboracion: Optional[str] = "planta"
    nivel_confianza: Optional[int] = 3
    fecha_ultima_evaluacion: Optional[date] = None
    fecha_ingreso: Optional[date] = None
    activo: bool

    model_config = {"from_attributes": True}
