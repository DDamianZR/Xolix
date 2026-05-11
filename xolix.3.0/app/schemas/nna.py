from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

# --- Pydantic sub-schemas for JSON fields ---
class FraseComunicada(BaseModel):
    id: str
    texto: str
    comunicada: bool
    notas: Optional[str] = None

class DiaComunData(BaseModel):
    quien_despierta: Optional[str] = None
    rutina_matutina: Optional[str] = None
    cuidador_dia: Optional[str] = None
    relaciones_externas: Optional[str] = None
    nna_es_central: Optional[str] = None        # "si"|"no"|"indeterminado"
    adulto_dificultad: Optional[str] = None     # "si"|"no"|"indeterminado"
    personas_mencionadas: List[str] = []

# --- CasoNNA ---
class CasoNNACreate(BaseModel):
    nna_nombre: str
    nna_edad: Optional[int] = None
    nna_genero: Optional[str] = None

class CasoNNAUpdate(BaseModel):
    nna_nombre: Optional[str] = None
    nna_edad: Optional[int] = None
    nna_genero: Optional[str] = None
    estado: Optional[str] = None

class CasoNNAResponse(BaseModel):
    id: int
    nna_nombre: str
    nna_edad: Optional[int] = None
    nna_genero: Optional[str] = None
    estado: str
    creador_id: int
    fecha_creacion: Optional[datetime] = None
    fecha_actualizacion: Optional[datetime] = None

    model_config = {"from_attributes": True}

# --- EntrevistaFamilia ---
class EntrevistaCreate(BaseModel):
    frases_comunicadas: Optional[List[FraseComunicada]] = None
    dia_comun: Optional[DiaComunData] = None
    grado_negacion: Optional[int] = 1
    observaciones_negacion: Optional[str] = None
    completada: Optional[bool] = False

class EntrevistaResponse(BaseModel):
    id: int
    caso_id: int
    fecha: Optional[datetime] = None
    frases_comunicadas: Optional[List[FraseComunicada]] = None
    dia_comun: Optional[DiaComunData] = None
    grado_negacion: int
    observaciones_negacion: Optional[str] = None
    completada: bool
    proceso_id: Optional[int] = None

    model_config = {"from_attributes": True}

# --- PersonaFamiliar ---
class PersonaFamiliarCreate(BaseModel):
    nombre: str
    edad: Optional[int] = None
    genero: Optional[str] = None
    rol_en_familia: Optional[str] = None
    tipo_simbolo: Optional[str] = "normal"
    observaciones: Optional[str] = None

class PersonaFamiliarUpdate(BaseModel):
    nombre: Optional[str] = None
    edad: Optional[int] = None
    genero: Optional[str] = None
    rol_en_familia: Optional[str] = None
    tipo_simbolo: Optional[str] = None
    observaciones: Optional[str] = None

class PersonaFamiliarResponse(BaseModel):
    id: int
    caso_id: int
    nombre: str
    edad: Optional[int] = None
    genero: Optional[str] = None
    rol_en_familia: Optional[str] = None
    tipo_simbolo: str
    observaciones: Optional[str] = None
    fecha_creacion: Optional[datetime] = None

    model_config = {"from_attributes": True}

# --- Familiograma ---
class FamiliogramaUpsert(BaseModel):
    grafo_json: Optional[Dict[str, Any]] = None
    imagen_url: Optional[str] = None

class FamiliogramaResponse(BaseModel):
    id: int
    caso_id: int
    grafo_json: Optional[Dict[str, Any]] = None
    imagen_url: Optional[str] = None
    fecha_actualizacion: Optional[datetime] = None

    model_config = {"from_attributes": True}

# --- ObservacionNoVerbal ---
class ObservacionCreate(BaseModel):
    persona_familiar_id: int
    postura: Optional[str] = None
    tono_voz: Optional[str] = None
    expresion_emocional: Optional[List[str]] = None
    estado_fisico: Optional[List[str]] = None
    nivel_resistencia: Optional[str] = None
    interpretacion_sugerida: Optional[str] = None

class ObservacionResponse(BaseModel):
    id: int
    caso_id: int
    persona_familiar_id: int
    persona_nombre: Optional[str] = None # Filled manually in service if needed
    postura: Optional[str] = None
    tono_voz: Optional[str] = None
    expresion_emocional: Optional[List[str]] = None
    estado_fisico: Optional[List[str]] = None
    nivel_resistencia: Optional[str] = None
    interpretacion_sugerida: Optional[str] = None
    registrada_por_id: int
    fecha_creacion: Optional[datetime] = None

    model_config = {"from_attributes": True}
