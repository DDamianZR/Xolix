from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


class ResponsableCreate(BaseModel):
    nombre: str
    cargo: Optional[str] = None
    telefono: Optional[str] = None
    correo: Optional[str] = None
    es_principal: Optional[bool] = False


class ResponsableResponse(ResponsableCreate):
    id: int
    actor_id: int
    fecha_creacion: Optional[datetime] = None

    model_config = {"from_attributes": True}


class HorarioCreate(BaseModel):
    dia_semana: str
    hora_inicio: Optional[str] = None
    hora_fin: Optional[str] = None


class HorarioResponse(HorarioCreate):
    id: int
    actor_id: int
    activo: bool

    model_config = {"from_attributes": True}


class RequisitoCreate(BaseModel):
    descripcion: str
    procedimiento_acceso: Optional[str] = None
    documentacion_requerida: Optional[str] = None


class RequisitoResponse(RequisitoCreate):
    id: int
    servicio_id: int

    model_config = {"from_attributes": True}


class ServicioCreate(BaseModel):
    derecho_id: Optional[int] = None
    nombre: str
    descripcion: Optional[str] = None
    tipo: str = "servicio"
    es_gratuito: bool = True
    costo: Optional[Decimal] = None
    disponibilidad: Optional[str] = None
    duracion_estimada: Optional[str] = None
    requisitos: List[RequisitoCreate] = []


class ServicioResponse(BaseModel):
    id: int
    actor_id: int
    derecho_id: Optional[int] = None
    nombre: str
    descripcion: Optional[str] = None
    tipo: str
    es_gratuito: bool
    costo: Optional[Decimal] = None
    disponibilidad: Optional[str] = None
    duracion_estimada: Optional[str] = None
    activo: bool
    requisitos: List[RequisitoResponse] = []

    model_config = {"from_attributes": True}


class ActorCreate(BaseModel):
    nombre: str
    tipo: str
    descripcion: Optional[str] = None
    direccion: Optional[str] = None
    municipio: Optional[str] = None
    estado: Optional[str] = None
    pais: str = "México"
    telefono: Optional[str] = None
    correo: Optional[str] = None
    sitio_web: Optional[str] = None
    redes_sociales: Optional[str] = None
    responsables: List[ResponsableCreate] = []
    horarios: List[HorarioCreate] = []
    servicios: List[ServicioCreate] = []


class ActorUpdate(BaseModel):
    nombre: Optional[str] = None
    tipo: Optional[str] = None
    descripcion: Optional[str] = None
    direccion: Optional[str] = None
    municipio: Optional[str] = None
    estado: Optional[str] = None
    pais: Optional[str] = None
    telefono: Optional[str] = None
    correo: Optional[str] = None
    sitio_web: Optional[str] = None
    redes_sociales: Optional[str] = None
    activo: Optional[bool] = None


class ActorListResponse(BaseModel):
    id: int
    nombre: str
    tipo: str
    descripcion: Optional[str] = None
    municipio: Optional[str] = None
    estado: Optional[str] = None
    telefono: Optional[str] = None
    correo: Optional[str] = None
    activo: bool

    model_config = {"from_attributes": True}


class ActorResponse(ActorListResponse):
    direccion: Optional[str] = None
    pais: Optional[str] = None
    sitio_web: Optional[str] = None
    redes_sociales: Optional[str] = None
    fecha_creacion: Optional[datetime] = None
    responsables: List[ResponsableResponse] = []
    horarios: List[HorarioResponse] = []
    servicios: List[ServicioResponse] = []

    model_config = {"from_attributes": True}
