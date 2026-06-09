from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime


class EvidenciaCreate(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    tipo_archivo: Optional[str] = None


class EvidenciaResponse(EvidenciaCreate):
    id: int
    diagnostico_id: int
    archivo_path: Optional[str] = None
    fecha_subida: Optional[datetime] = None

    model_config = {"from_attributes": True}


class IndicadorEvalCreate(BaseModel):
    indicador_id: int
    valor: Optional[str] = None
    observacion: Optional[str] = None
    vulnerado: bool = False


class IndicadorEvalResponse(IndicadorEvalCreate):
    id: int
    diagnostico_id: int
    fecha_creacion: Optional[datetime] = None

    model_config = {"from_attributes": True}


class DerechoVulneradoCreate(BaseModel):
    derecho_id: int
    severidad: str = "moderada"
    recomendacion: Optional[str] = None


class DerechoVulneradoResponse(DerechoVulneradoCreate):
    id: int
    diagnostico_id: int
    generado_automaticamente: bool
    derecho_nombre: Optional[str] = None
    fecha_creacion: Optional[datetime] = None

    model_config = {"from_attributes": True}


class DiagnosticoCreate(BaseModel):
    caso_nna_id: int
    tipo: str
    fecha: date
    observaciones: Optional[str] = None
    indicadores: List[IndicadorEvalCreate] = []


class DiagnosticoUpdate(BaseModel):
    observaciones: Optional[str] = None
    completado: Optional[bool] = None


class DiagnosticoResponse(BaseModel):
    id: int
    caso_nna_id: int
    tipo: str
    fecha: date
    responsable_id: Optional[int] = None
    observaciones: Optional[str] = None
    completado: bool
    fecha_creacion: Optional[datetime] = None
    evidencias: List[EvidenciaResponse] = []
    indicadores_eval: List[IndicadorEvalResponse] = []
    derechos_vulnerados: List[DerechoVulneradoResponse] = []

    model_config = {"from_attributes": True}
