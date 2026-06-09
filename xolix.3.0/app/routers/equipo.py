from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.dependencies import get_db, get_current_user, require_role
from app.schemas.equipo import (
    MiembroCreate, MiembroUpdate, MiembroResponse,
    AsignarResponsableRequest,
)
from app.services import equipo_service

router = APIRouter(prefix="/api/nna/casos", tags=["Equipo Multidisciplinario"])


@router.get("/{caso_id}/equipo", response_model=List[MiembroResponse])
def listar_equipo(caso_id: int, db: Session = Depends(get_db),
                  current_user: dict = Depends(get_current_user)):
    return equipo_service.listar_equipo(db, caso_id)


@router.post("/{caso_id}/equipo", response_model=MiembroResponse)
def agregar_miembro(caso_id: int, data: MiembroCreate,
                    db: Session = Depends(get_db),
                    current_user: dict = Depends(require_role(
                        "trabajador_social", "director", "coordinador"))):
    return equipo_service.agregar_miembro(
        db, caso_id,
        usuario_id=data.usuario_id,
        rol_en_equipo=data.rol_en_equipo,
        asignado_por_id=current_user["user_id"],
        actor_rol=current_user["rol"],
        observaciones=data.observaciones,
    )


@router.patch("/{caso_id}/equipo/{usuario_id}", response_model=MiembroResponse)
def cambiar_rol(caso_id: int, usuario_id: int, data: MiembroUpdate,
                db: Session = Depends(get_db),
                current_user: dict = Depends(require_role(
                    "trabajador_social", "director", "coordinador"))):
    return equipo_service.cambiar_rol_miembro(
        db, caso_id, usuario_id,
        nuevo_rol=data.rol_en_equipo,
        actor_id=current_user["user_id"],
        actor_rol=current_user["rol"],
    )


@router.delete("/{caso_id}/equipo/{usuario_id}")
def quitar_miembro(caso_id: int, usuario_id: int,
                   db: Session = Depends(get_db),
                   current_user: dict = Depends(require_role(
                       "trabajador_social", "director", "coordinador"))):
    equipo_service.quitar_miembro(
        db, caso_id, usuario_id,
        actor_id=current_user["user_id"],
        actor_rol=current_user["rol"],
    )
    return {"ok": True}


@router.put("/{caso_id}/responsable")
def asignar_responsable(caso_id: int, data: AsignarResponsableRequest,
                        db: Session = Depends(get_db),
                        current_user: dict = Depends(require_role("director", "coordinador"))):
    equipo_service.asignar_responsable(
        db, caso_id,
        ts_id=data.responsable_id,
        actor_id=current_user["user_id"],
        actor_rol=current_user["rol"],
    )
    return {"ok": True, "responsable_id": data.responsable_id}
