from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_current_user, require_role
from app.schemas.actor import (
    ActorCreate, ActorUpdate, ActorResponse, ActorListResponse,
    ResponsableCreate, ResponsableResponse,
    ServicioCreate, ServicioResponse,
)
from app.services import actor_service

router = APIRouter(prefix="/api/actores", tags=["Actores"])


@router.get("/", response_model=List[ActorListResponse])
def listar_actores(
    municipio: Optional[str] = Query(None),
    estado: Optional[str] = Query(None),
    derecho_id: Optional[int] = Query(None),
    tipo: Optional[str] = Query(None),
    es_gratuito: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    return actor_service.listar_actores(db, municipio, estado, derecho_id, tipo, es_gratuito)


@router.get("/{actor_id}", response_model=ActorResponse)
def obtener_actor(
    actor_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    return actor_service.obtener_actor(db, actor_id)


@router.post("/", response_model=ActorResponse)
def crear_actor(
    data: ActorCreate,
    db: Session = Depends(get_db),
    _: dict = Depends(require_role("director", "coordinador")),
):
    payload = data.model_dump()
    return actor_service.crear_actor(db, payload)


@router.put("/{actor_id}", response_model=ActorResponse)
def actualizar_actor(
    actor_id: int,
    data: ActorUpdate,
    db: Session = Depends(get_db),
    _: dict = Depends(require_role("director", "coordinador")),
):
    return actor_service.actualizar_actor(db, actor_id, data.model_dump(exclude_unset=True))


@router.delete("/{actor_id}")
def eliminar_actor(
    actor_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(require_role("director", "coordinador")),
):
    actor_service.eliminar_actor(db, actor_id)
    return {"mensaje": "Actor desactivado"}


@router.post("/{actor_id}/responsables", response_model=ResponsableResponse)
def agregar_responsable(
    actor_id: int,
    data: ResponsableCreate,
    db: Session = Depends(get_db),
    _: dict = Depends(require_role("director", "coordinador")),
):
    return actor_service.agregar_responsable(db, actor_id, data.model_dump())


@router.post("/{actor_id}/servicios", response_model=ServicioResponse)
def agregar_servicio(
    actor_id: int,
    data: ServicioCreate,
    db: Session = Depends(get_db),
    _: dict = Depends(require_role("director", "coordinador")),
):
    return actor_service.agregar_servicio(db, actor_id, data.model_dump())


@router.delete("/servicios/{servicio_id}")
def eliminar_servicio(
    servicio_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(require_role("director", "coordinador")),
):
    actor_service.eliminar_servicio(db, servicio_id)
    return {"mensaje": "Servicio desactivado"}
