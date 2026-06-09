from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import date, datetime


class SeguimientoCreate(BaseModel):
    fecha_seguimiento: date
    descripcion_avance: str
    porcentaje_cumplimiento: int = 0
    observaciones: Optional[str] = None
    evidencias: Optional[List[Any]] = None


class SeguimientoResponse(SeguimientoCreate):
    id: int
    medida_id: int
    registrado_por_id: Optional[int] = None
    fecha_creacion: Optional[datetime] = None

    model_config = {"from_attributes": True}


class MedidaCreate(BaseModel):
    tipo: str = "otra"
    descripcion: str
    responsable_id: Optional[int] = None
    actor_id: Optional[int] = None
    recursos_requeridos: Optional[str] = None
    fecha_inicio: Optional[date] = None
    fecha_limite: Optional[date] = None


class MedidaUpdate(BaseModel):
    tipo: Optional[str] = None
    descripcion: Optional[str] = None
    responsable_id: Optional[int] = None
    actor_id: Optional[int] = None
    recursos_requeridos: Optional[str] = None
    estado: Optional[str] = None
    porcentaje_avance: Optional[int] = None
    fecha_inicio: Optional[date] = None
    fecha_limite: Optional[date] = None


class MedidaResponse(MedidaCreate):
    id: int
    plan_id: int
    estado: str
    porcentaje_avance: int
    fecha_creacion: Optional[datetime] = None
    seguimientos: List[SeguimientoResponse] = []

    model_config = {"from_attributes": True}


class PlanCreate(BaseModel):
    caso_nna_id: int
    objetivo: str
    derechos_afectados: Optional[List[int]] = None
    responsable_id: Optional[int] = None
    fecha_inicio: Optional[date] = None
    fecha_termino: Optional[date] = None
    observaciones: Optional[str] = None
    medidas: List[MedidaCreate] = []


class PlanUpdate(BaseModel):
    objetivo: Optional[str] = None
    derechos_afectados: Optional[List[int]] = None
    responsable_id: Optional[int] = None
    fecha_inicio: Optional[date] = None
    fecha_termino: Optional[date] = None
    estado: Optional[str] = None
    observaciones: Optional[str] = None


class PlanResponse(BaseModel):
    id: int
    caso_nna_id: int
    objetivo: str
    derechos_afectados: Optional[List[int]] = None
    responsable_id: Optional[int] = None
    fecha_inicio: Optional[date] = None
    fecha_termino: Optional[date] = None
    estado: str
    observaciones: Optional[str] = None
    fecha_creacion: Optional[datetime] = None
    medidas: List[MedidaResponse] = []

    model_config = {"from_attributes": True}
