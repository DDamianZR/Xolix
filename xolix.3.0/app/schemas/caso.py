from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date


# ── Hecho Victimal ─────────────────────────

class HechoVictimalCreate(BaseModel):
    victima_nombres: Optional[str] = None
    victima_apellido_paterno: Optional[str] = None
    victima_apellido_materno: Optional[str] = None
    victima_curp: Optional[str] = None
    menor_nombres: Optional[str] = None
    menor_apellido_paterno: Optional[str] = None
    menor_apellido_materno: Optional[str] = None
    menor_curp: Optional[str] = None
    edad_menor: Optional[int] = None
    fecha_incidente: Optional[date] = None
    ubicacion: Optional[str] = None
    descripcion_delito: Optional[str] = None
    tipo_violencia: Optional[str] = None
    referencia_juridica: Optional[str] = None
    referencia_fud: Optional[str] = None
    consideraciones: Optional[str] = None


class HechoVictimalResponse(BaseModel):
    id: int
    victima_nombres: Optional[str] = None
    victima_apellido_paterno: Optional[str] = None
    victima_apellido_materno: Optional[str] = None
    victima_curp: Optional[str] = None
    menor_nombres: Optional[str] = None
    menor_apellido_paterno: Optional[str] = None
    menor_apellido_materno: Optional[str] = None
    menor_curp: Optional[str] = None
    edad_menor: Optional[int] = None
    fecha_incidente: Optional[date] = None
    ubicacion: Optional[str] = None
    descripcion_delito: Optional[str] = None
    tipo_violencia: Optional[str] = None
    referencia_juridica: Optional[str] = None
    referencia_fud: Optional[str] = None
    fecha_creacion_expediente: Optional[datetime] = None
    consideraciones: Optional[str] = None

    model_config = {"from_attributes": True}


# ── Participante ───────────────────────────

class ParticipanteCreate(BaseModel):
    usuario_id: int
    area: str
    permiso: Optional[str] = "escritura"


class ParticipanteResponse(BaseModel):
    id: int
    usuario_id: int
    usuario_nombre: Optional[str] = None
    area: str
    permiso: str

    model_config = {"from_attributes": True}


# ── Nota ───────────────────────────────────

class NotaCreate(BaseModel):
    area: Optional[str] = "general"
    contenido: str
    privada: Optional[bool] = False
    etiquetas: Optional[list[str]] = []


class NotaResponse(BaseModel):
    id: int
    caso_id: int
    autor_id: int
    autor_nombre: Optional[str] = None
    autor_area: Optional[str] = None
    area: str
    contenido: str
    privada: bool
    etiquetas: Optional[list[str]] = []
    fecha_creacion: Optional[datetime] = None
    fecha_actualizacion: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ── Documento ──────────────────────────────

class DocumentoResponse(BaseModel):
    id: int
    nombre: str
    tipo_archivo: str
    categoria: str
    version: int
    subido_por_nombre: Optional[str] = None
    fecha_subida: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ── Caso ───────────────────────────────────

class CasoCreate(BaseModel):
    titulo: str
    descripcion: Optional[str] = None
    estado: Optional[str] = "activo"
    nivel_riesgo: Optional[str] = "medio"
    hecho_victimal: Optional[HechoVictimalCreate] = None
    participante_ids: Optional[list[dict]] = []


class CasoUpdate(BaseModel):
    titulo: Optional[str] = None
    descripcion: Optional[str] = None
    estado: Optional[str] = None
    nivel_riesgo: Optional[str] = None


class CasoListResponse(BaseModel):
    id: int
    folio: str
    titulo: str
    estado: str
    nivel_riesgo: str
    fecha_creacion: Optional[datetime] = None
    participantes_count: int = 0
    notas_count: int = 0
    documentos_count: int = 0

    model_config = {"from_attributes": True}


class CasoDetailResponse(BaseModel):
    id: int
    folio: str
    titulo: str
    descripcion: Optional[str] = None
    estado: str
    nivel_riesgo: str
    creador_id: int
    fecha_creacion: Optional[datetime] = None
    hecho_victimal: Optional[HechoVictimalResponse] = None
    participantes: list[ParticipanteResponse] = []
    notas: list[NotaResponse] = []
    documentos: list[DocumentoResponse] = []

    model_config = {"from_attributes": True}
