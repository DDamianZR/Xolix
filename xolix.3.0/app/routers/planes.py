from fastapi import APIRouter, Depends
from typing import List
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_current_user, require_role
from app.schemas.plan import (
    PlanCreate, PlanUpdate, PlanResponse,
    MedidaCreate, MedidaUpdate, MedidaResponse,
    SeguimientoCreate, SeguimientoResponse,
)
from app.services import plan_service

router = APIRouter(prefix="/api/planes", tags=["Planes de Restitución"])


# ── Planes ───────────────────────────────────

@router.get("/caso/{caso_nna_id}", response_model=List[PlanResponse])
def listar_planes(
    caso_nna_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    return plan_service.listar_planes(db, caso_nna_id)


@router.get("/{plan_id}", response_model=PlanResponse)
def obtener_plan(
    plan_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    return plan_service.obtener_plan(db, plan_id)


@router.post("/", response_model=PlanResponse)
def crear_plan(
    data: PlanCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    return plan_service.crear_plan(db, data.model_dump(), current_user.get("user_id"))


@router.put("/{plan_id}", response_model=PlanResponse)
def actualizar_plan(
    plan_id: int,
    data: PlanUpdate,
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    return plan_service.actualizar_plan(db, plan_id, data.model_dump(exclude_unset=True))


@router.delete("/{plan_id}")
def eliminar_plan(
    plan_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(require_role("director", "coordinador")),
):
    plan_service.eliminar_plan(db, plan_id)
    return {"mensaje": "Plan eliminado"}


# ── Medidas ──────────────────────────────────

@router.post("/{plan_id}/medidas", response_model=MedidaResponse)
def agregar_medida(
    plan_id: int,
    data: MedidaCreate,
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    return plan_service.agregar_medida(db, plan_id, data.model_dump())


@router.put("/medidas/{medida_id}", response_model=MedidaResponse)
def actualizar_medida(
    medida_id: int,
    data: MedidaUpdate,
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    return plan_service.actualizar_medida(db, medida_id, data.model_dump(exclude_unset=True))


# ── Seguimientos ─────────────────────────────

@router.post("/medidas/{medida_id}/seguimientos", response_model=SeguimientoResponse)
def registrar_seguimiento(
    medida_id: int,
    data: SeguimientoCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    return plan_service.registrar_seguimiento(
        db, medida_id, data.model_dump(), current_user.get("user_id")
    )
