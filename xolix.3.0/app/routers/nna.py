from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.dependencies import get_db, get_current_user, require_role
from app.schemas.nna import (
    CasoNNACreate, CasoNNAUpdate, CasoNNAResponse,
    EntrevistaCreate, EntrevistaResponse,
    PersonaFamiliarCreate, PersonaFamiliarUpdate, PersonaFamiliarResponse,
    FamiliogramaUpsert, FamiliogramaResponse,
    ObservacionCreate, ObservacionResponse,
    RelacionFamiliarCreate, RelacionFamiliarUpdate, RelacionFamiliarResponse,
    HistorialFamiliogramaResponse,
    TutorCreate, TutorResponse,
    DatosMedicosCreate, DatosMedicosResponse,
)
from app.services import nna_service

router = APIRouter(prefix="/api/nna", tags=["Protección NNA"])

# ── Casos NNA ────────────────────────────────

@router.post("/casos", response_model=CasoNNAResponse)
def crear_caso(data: CasoNNACreate, db: Session = Depends(get_db),
               current_user: dict = Depends(get_current_user)):
    return nna_service.crear_caso_nna(db, data.model_dump(), current_user.get("user_id"))

@router.get("/casos", response_model=List[CasoNNAResponse])
def listar_casos(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    return nna_service.listar_casos_nna(db, current_user.get("user_id"), current_user.get("rol", ""))

@router.get("/casos/{caso_id}", response_model=CasoNNAResponse)
def obtener_caso(caso_id: int, db: Session = Depends(get_db),
                 current_user: dict = Depends(get_current_user)):
    return nna_service.obtener_caso_nna(db, caso_id, current_user.get("user_id"), current_user.get("rol", ""))

@router.put("/casos/{caso_id}", response_model=CasoNNAResponse)
def actualizar_caso(caso_id: int, data: CasoNNAUpdate, db: Session = Depends(get_db),
                    current_user: dict = Depends(get_current_user)):
    nna_service.obtener_caso_nna(db, caso_id, current_user.get("user_id"), current_user.get("rol", ""))
    return nna_service.actualizar_caso_nna(db, caso_id, data.model_dump(exclude_unset=True))

@router.delete("/casos/{caso_id}")
def eliminar_caso(caso_id: int, db: Session = Depends(get_db),
                  _current_user: dict = Depends(require_role("director", "coordinador"))):
    nna_service.eliminar_caso_nna(db, caso_id)
    return {"mensaje": "Caso NNA eliminado"}

# ── Entrevista ───────────────────────────────

@router.post("/casos/{caso_id}/entrevista", response_model=EntrevistaResponse)
def guardar_entrevista(caso_id: int, data: EntrevistaCreate, db: Session = Depends(get_db),
                       current_user: dict = Depends(get_current_user)):
    nna_service.obtener_caso_nna(db, caso_id, current_user.get("user_id"), current_user.get("rol", ""))
    return nna_service.crear_o_actualizar_entrevista(db, caso_id, data.model_dump(exclude_unset=True))

@router.get("/casos/{caso_id}/entrevista")
def obtener_entrevista(caso_id: int, db: Session = Depends(get_db),
                       current_user: dict = Depends(get_current_user)):
    nna_service.obtener_caso_nna(db, caso_id, current_user.get("user_id"), current_user.get("rol", ""))
    entrevista = nna_service.obtener_entrevista(db, caso_id)
    if not entrevista:
        return None
    return EntrevistaResponse.model_validate(entrevista)

# ── Personas ─────────────────────────────────

@router.post("/casos/{caso_id}/personas", response_model=PersonaFamiliarResponse)
def agregar_persona(caso_id: int, data: PersonaFamiliarCreate, db: Session = Depends(get_db),
                    current_user: dict = Depends(get_current_user)):
    nna_service.obtener_caso_nna(db, caso_id, current_user.get("user_id"), current_user.get("rol", ""))
    return nna_service.crear_persona(db, caso_id, data.model_dump())

@router.get("/casos/{caso_id}/personas", response_model=List[PersonaFamiliarResponse])
def listar_personas(caso_id: int, db: Session = Depends(get_db),
                    current_user: dict = Depends(get_current_user)):
    nna_service.obtener_caso_nna(db, caso_id, current_user.get("user_id"), current_user.get("rol", ""))
    return nna_service.listar_personas(db, caso_id)

@router.get("/casos/{caso_id}/personas/{persona_id}", response_model=PersonaFamiliarResponse)
def obtener_persona(caso_id: int, persona_id: int, db: Session = Depends(get_db),
                    current_user: dict = Depends(get_current_user)):
    nna_service.obtener_caso_nna(db, caso_id, current_user.get("user_id"), current_user.get("rol", ""))
    return nna_service.obtener_persona(db, persona_id)

@router.put("/casos/{caso_id}/personas/{persona_id}", response_model=PersonaFamiliarResponse)
def actualizar_persona(caso_id: int, persona_id: int, data: PersonaFamiliarUpdate,
                       db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    nna_service.obtener_caso_nna(db, caso_id, current_user.get("user_id"), current_user.get("rol", ""))
    return nna_service.actualizar_persona(db, persona_id, data.model_dump(exclude_unset=True))

@router.delete("/casos/{caso_id}/personas/{persona_id}")
def eliminar_persona(caso_id: int, persona_id: int, db: Session = Depends(get_db),
                     current_user: dict = Depends(get_current_user)):
    nna_service.obtener_caso_nna(db, caso_id, current_user.get("user_id"), current_user.get("rol", ""))
    nna_service.eliminar_persona(db, persona_id)
    return {"mensaje": "Persona eliminada"}

# ── Familiograma ─────────────────────────────

@router.post("/casos/{caso_id}/familiograma", response_model=FamiliogramaResponse)
def guardar_familiograma(caso_id: int, data: FamiliogramaUpsert, db: Session = Depends(get_db),
                         current_user: dict = Depends(get_current_user)):
    nna_service.obtener_caso_nna(db, caso_id, current_user.get("user_id"), current_user.get("rol", ""))
    return nna_service.upsert_familiograma(
        db, caso_id, data.grafo_json, data.imagen_url,
        notas_version=data.notas_version,
        modificado_por_id=current_user.get("user_id")
    )

@router.get("/casos/{caso_id}/familiograma")
def obtener_familiograma(caso_id: int, db: Session = Depends(get_db),
                         current_user: dict = Depends(get_current_user)):
    nna_service.obtener_caso_nna(db, caso_id, current_user.get("user_id"), current_user.get("rol", ""))
    familiograma = nna_service.obtener_familiograma(db, caso_id)
    if not familiograma:
        return None
    return FamiliogramaResponse.model_validate(familiograma)

@router.get("/casos/{caso_id}/familiograma/historial")
def obtener_historial(caso_id: int, db: Session = Depends(get_db),
                      current_user: dict = Depends(get_current_user)):
    """Devuelve todas las versiones guardadas del familiograma."""
    nna_service.obtener_caso_nna(db, caso_id, current_user.get("user_id"), current_user.get("rol", ""))
    return nna_service.obtener_historial_familiograma(db, caso_id)

@router.post("/casos/{caso_id}/familiograma/historial/{historial_id}/restaurar",
             response_model=FamiliogramaResponse)
def restaurar_version(caso_id: int, historial_id: int, db: Session = Depends(get_db),
                      current_user: dict = Depends(get_current_user)):
    """Restaura el grafo a una versión anterior."""
    nna_service.obtener_caso_nna(db, caso_id, current_user.get("user_id"), current_user.get("rol", ""))
    return nna_service.restaurar_version_familiograma(
        db, caso_id, historial_id, current_user.get("user_id")
    )

@router.get("/casos/{caso_id}/familiograma/exportar")
def exportar_familiograma(caso_id: int, db: Session = Depends(get_db),
                          current_user: dict = Depends(get_current_user)):
    """Exporta datos completos del familiograma (JSON)."""
    nna_service.obtener_caso_nna(db, caso_id, current_user.get("user_id"), current_user.get("rol", ""))
    return nna_service.exportar_familiograma(db, caso_id)

# ── Relaciones Familiares ────────────────────

@router.post("/casos/{caso_id}/relaciones", response_model=RelacionFamiliarResponse)
def crear_relacion(caso_id: int, data: RelacionFamiliarCreate, db: Session = Depends(get_db),
                   current_user: dict = Depends(get_current_user)):
    nna_service.obtener_caso_nna(db, caso_id, current_user.get("user_id"), current_user.get("rol", ""))
    relacion = nna_service.crear_relacion(db, caso_id, data.model_dump())
    return {
        "id": relacion.id, "caso_id": relacion.caso_id,
        "persona_origen_id": relacion.persona_origen_id,
        "persona_destino_id": relacion.persona_destino_id,
        "persona_origen_nombre": relacion.persona_origen.nombre if relacion.persona_origen else None,
        "persona_destino_nombre": relacion.persona_destino.nombre if relacion.persona_destino else None,
        "tipo_relacion": relacion.tipo_relacion.value,
        "descripcion": relacion.descripcion,
        "bidireccional": relacion.bidireccional,
        "fecha_creacion": relacion.fecha_creacion,
    }

@router.get("/casos/{caso_id}/relaciones")
def listar_relaciones(caso_id: int, db: Session = Depends(get_db),
                      current_user: dict = Depends(get_current_user)):
    nna_service.obtener_caso_nna(db, caso_id, current_user.get("user_id"), current_user.get("rol", ""))
    return nna_service.listar_relaciones(db, caso_id)

@router.put("/casos/{caso_id}/relaciones/{relacion_id}")
def actualizar_relacion(caso_id: int, relacion_id: int, data: RelacionFamiliarUpdate,
                         db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    nna_service.obtener_caso_nna(db, caso_id, current_user.get("user_id"), current_user.get("rol", ""))
    relacion = nna_service.actualizar_relacion(db, relacion_id, caso_id, data.model_dump(exclude_unset=True))
    return {"mensaje": "Relación actualizada", "id": relacion.id}

@router.delete("/casos/{caso_id}/relaciones/{relacion_id}")
def eliminar_relacion(caso_id: int, relacion_id: int, db: Session = Depends(get_db),
                      current_user: dict = Depends(get_current_user)):
    nna_service.obtener_caso_nna(db, caso_id, current_user.get("user_id"), current_user.get("rol", ""))
    nna_service.eliminar_relacion(db, relacion_id, caso_id)
    return {"mensaje": "Relación eliminada"}

# ── Observaciones ────────────────────────────

@router.post("/casos/{caso_id}/observaciones", response_model=ObservacionResponse)
def registrar_observacion(caso_id: int, data: ObservacionCreate, db: Session = Depends(get_db),
                          current_user: dict = Depends(get_current_user)):
    nna_service.obtener_caso_nna(db, caso_id, current_user.get("user_id"), current_user.get("rol", ""))
    obs = nna_service.crear_observacion(db, caso_id, data.model_dump(), current_user.get("user_id"))
    return ObservacionResponse.model_validate(obs)

@router.get("/casos/{caso_id}/observaciones", response_model=List[ObservacionResponse])
def listar_observaciones(caso_id: int, db: Session = Depends(get_db),
                         current_user: dict = Depends(get_current_user)):
    nna_service.obtener_caso_nna(db, caso_id, current_user.get("user_id"), current_user.get("rol", ""))
    return nna_service.listar_observaciones(db, caso_id)

# ── Plan de Acción ───────────────────────────

@router.post("/casos/{caso_id}/plan-accion")
def generar_plan(caso_id: int, db: Session = Depends(get_db),
                 current_user: dict = Depends(get_current_user)):
    nna_service.obtener_caso_nna(db, caso_id, current_user.get("user_id"), current_user.get("rol", ""))
    return nna_service.generar_plan_accion(db, caso_id, current_user.get("user_id"))

@router.get("/casos/{caso_id}/plan-accion")
def obtener_plan(caso_id: int, db: Session = Depends(get_db),
                 current_user: dict = Depends(get_current_user)):
    nna_service.obtener_caso_nna(db, caso_id, current_user.get("user_id"), current_user.get("rol", ""))
    plan = nna_service.obtener_plan_accion(db, caso_id)
    if not plan:
        return None
    return plan

# ── Tutor ────────────────────────────────────

@router.post("/casos/{caso_id}/tutor", response_model=TutorResponse)
def guardar_tutor(caso_id: int, data: TutorCreate, db: Session = Depends(get_db),
                  current_user: dict = Depends(get_current_user)):
    nna_service.obtener_caso_nna(db, caso_id, current_user.get("user_id"), current_user.get("rol", ""))
    return nna_service.upsert_tutor(db, caso_id, data.model_dump())

@router.get("/casos/{caso_id}/tutor", response_model=TutorResponse)
def obtener_tutor(caso_id: int, db: Session = Depends(get_db),
                  current_user: dict = Depends(get_current_user)):
    nna_service.obtener_caso_nna(db, caso_id, current_user.get("user_id"), current_user.get("rol", ""))
    return nna_service.obtener_tutor(db, caso_id)

# ── Datos Médicos ────────────────────────────

@router.post("/casos/{caso_id}/datos-medicos", response_model=DatosMedicosResponse)
def guardar_datos_medicos(caso_id: int, data: DatosMedicosCreate, db: Session = Depends(get_db),
                          current_user: dict = Depends(get_current_user)):
    nna_service.obtener_caso_nna(db, caso_id, current_user.get("user_id"), current_user.get("rol", ""))
    return nna_service.upsert_datos_medicos(db, caso_id, data.model_dump())

@router.get("/casos/{caso_id}/datos-medicos", response_model=DatosMedicosResponse)
def obtener_datos_medicos(caso_id: int, db: Session = Depends(get_db),
                          current_user: dict = Depends(get_current_user)):
    nna_service.obtener_caso_nna(db, caso_id, current_user.get("user_id"), current_user.get("rol", ""))
    return nna_service.obtener_datos_medicos(db, caso_id)
