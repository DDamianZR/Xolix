from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class DerechoCreate(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    categoria: str = "proteccion"
    articulo_referencia: Optional[str] = None


class DerechoUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    categoria: Optional[str] = None
    articulo_referencia: Optional[str] = None
    activo: Optional[bool] = None


class IndicadorBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    tipo_evaluacion: Optional[str] = "si_no"


class IndicadorResponse(IndicadorBase):
    id: int
    derecho_id: int
    activo: bool
    fecha_creacion: Optional[datetime] = None

    model_config = {"from_attributes": True}


class DerechoResponse(DerechoCreate):
    id: int
    activo: bool
    fecha_creacion: Optional[datetime] = None
    indicadores: List[IndicadorResponse] = []

    model_config = {"from_attributes": True}


class IndicadorCreate(IndicadorBase):
    derecho_id: int


class IndicadorUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    tipo_evaluacion: Optional[str] = None
    activo: Optional[bool] = None
