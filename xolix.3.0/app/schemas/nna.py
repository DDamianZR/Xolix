from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, date

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

# --- Tutor ---
class TutorCreate(BaseModel):
    nombre: str
    apellido_paterno: Optional[str] = None
    apellido_materno: Optional[str] = None
    curp: Optional[str] = None
    rfc: Optional[str] = None
    parentesco: Optional[str] = None
    telefono: Optional[str] = None
    correo: Optional[str] = None
    direccion: Optional[str] = None
    ocupacion: Optional[str] = None
    documento_identificacion: Optional[str] = None
    numero_documento: Optional[str] = None

class TutorResponse(TutorCreate):
    id: int
    caso_id: int
    fecha_creacion: Optional[datetime] = None

    model_config = {"from_attributes": True}

# --- DatosMedicos ---
class VacunaItem(BaseModel):
    vacuna: str
    fecha: Optional[str] = None
    dosis: Optional[str] = None

class DatosMedicosCreate(BaseModel):
    historial_medico: Optional[str] = None
    alergias: Optional[str] = None
    discapacidades: Optional[str] = None
    cartilla_vacunacion: Optional[List[VacunaItem]] = None
    tipo_sangre: Optional[str] = None
    medico_responsable: Optional[str] = None
    institucion_medica: Optional[str] = None

class DatosMedicosResponse(DatosMedicosCreate):
    id: int
    caso_id: int
    fecha_creacion: Optional[datetime] = None

    model_config = {"from_attributes": True}

# --- CasoNNA ---
class CasoNNACreate(BaseModel):
    nna_nombre: str
    nna_curp: Optional[str] = None
    nna_fecha_nacimiento: Optional[str] = None
    nna_edad: Optional[int] = None
    nna_genero: Optional[str] = None
    nna_nacionalidad: Optional[str] = "Mexicana"
    nna_estado_civil: Optional[str] = None

class CasoNNAUpdate(BaseModel):
    nna_nombre: Optional[str] = None
    nna_curp: Optional[str] = None
    nna_fecha_nacimiento: Optional[str] = None
    nna_edad: Optional[int] = None
    nna_genero: Optional[str] = None
    nna_nacionalidad: Optional[str] = None
    nna_estado_civil: Optional[str] = None
    estado: Optional[str] = None

class CasoNNAResponse(BaseModel):
    id: int
    nna_nombre: str
    nna_curp: Optional[str] = None
    nna_fecha_nacimiento: Optional[Any] = None
    nna_edad: Optional[int] = None
    nna_genero: Optional[str] = None
    nna_nacionalidad: Optional[str] = None
    nna_estado_civil: Optional[str] = None
    estado: str
    creador_id: int
    responsable_id: Optional[int] = None
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
    # Campos extendidos
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    ocupacion: Optional[str] = None
    escolaridad: Optional[str] = None
    estado_salud: Optional[str] = None
    vive_con_nna: Optional[bool] = False
    es_responsable_legal: Optional[bool] = False

class PersonaFamiliarUpdate(BaseModel):
    nombre: Optional[str] = None
    edad: Optional[int] = None
    genero: Optional[str] = None
    rol_en_familia: Optional[str] = None
    tipo_simbolo: Optional[str] = None
    observaciones: Optional[str] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    ocupacion: Optional[str] = None
    escolaridad: Optional[str] = None
    estado_salud: Optional[str] = None
    vive_con_nna: Optional[bool] = None
    es_responsable_legal: Optional[bool] = None

class PersonaFamiliarResponse(BaseModel):
    id: int
    caso_id: int
    nombre: str
    edad: Optional[int] = None
    genero: Optional[str] = None
    rol_en_familia: Optional[str] = None
    tipo_simbolo: str
    observaciones: Optional[str] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    ocupacion: Optional[str] = None
    escolaridad: Optional[str] = None
    estado_salud: Optional[str] = None
    vive_con_nna: bool = False
    es_responsable_legal: bool = False
    fecha_creacion: Optional[datetime] = None

    model_config = {"from_attributes": True}

# --- Familiograma ---
class FamiliogramaUpsert(BaseModel):
    grafo_json: Optional[Dict[str, Any]] = None
    imagen_url: Optional[str] = None
    notas_version: Optional[str] = None  # Nota descriptiva del cambio

class FamiliogramaResponse(BaseModel):
    id: int
    caso_id: int
    grafo_json: Optional[Dict[str, Any]] = None
    imagen_url: Optional[str] = None
    fecha_actualizacion: Optional[datetime] = None

    model_config = {"from_attributes": True}

# --- HistorialFamiliograma ---
class HistorialFamiliogramaResponse(BaseModel):
    id: int
    familiograma_id: int
    caso_id: int
    version: int
    grafo_json: Optional[Dict[str, Any]] = None
    modificado_por_id: Optional[int] = None
    modificado_por_nombre: Optional[str] = None
    notas_version: Optional[str] = None
    fecha: Optional[datetime] = None

    model_config = {"from_attributes": True}

# --- RelacionFamiliar ---
class RelacionFamiliarCreate(BaseModel):
    persona_origen_id: int
    persona_destino_id: int
    tipo_relacion: str = "biologica"
    descripcion: Optional[str] = None
    bidireccional: Optional[bool] = True

class RelacionFamiliarUpdate(BaseModel):
    tipo_relacion: Optional[str] = None
    descripcion: Optional[str] = None
    bidireccional: Optional[bool] = None

class RelacionFamiliarResponse(BaseModel):
    id: int
    caso_id: int
    persona_origen_id: int
    persona_destino_id: int
    persona_origen_nombre: Optional[str] = None
    persona_destino_nombre: Optional[str] = None
    tipo_relacion: str
    descripcion: Optional[str] = None
    bidireccional: bool
    fecha_creacion: Optional[datetime] = None

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
