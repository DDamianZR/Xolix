from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_current_user, require_role
from app.schemas.catalogo import (
    DerechoCreate, DerechoUpdate, DerechoResponse,
    IndicadorCreate, IndicadorUpdate, IndicadorResponse,
)
from app.services import catalogo_service

router = APIRouter(prefix="/api/catalogo", tags=["Catálogo"])


# ── Derechos ──────────────────────────────────

@router.get("/derechos", response_model=List[DerechoResponse])
def listar_derechos(
    activos_only: bool = Query(True),
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    return catalogo_service.listar_derechos(db, activos_only)


@router.get("/derechos/{derecho_id}", response_model=DerechoResponse)
def obtener_derecho(
    derecho_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    return catalogo_service.obtener_derecho(db, derecho_id)


@router.post("/derechos", response_model=DerechoResponse)
def crear_derecho(
    data: DerechoCreate,
    db: Session = Depends(get_db),
    _: dict = Depends(require_role("director", "coordinador")),
):
    return catalogo_service.crear_derecho(db, data.model_dump())


@router.put("/derechos/{derecho_id}", response_model=DerechoResponse)
def actualizar_derecho(
    derecho_id: int,
    data: DerechoUpdate,
    db: Session = Depends(get_db),
    _: dict = Depends(require_role("director", "coordinador")),
):
    return catalogo_service.actualizar_derecho(db, derecho_id, data.model_dump(exclude_unset=True))


@router.delete("/derechos/{derecho_id}")
def eliminar_derecho(
    derecho_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(require_role("director")),
):
    catalogo_service.eliminar_derecho(db, derecho_id)
    return {"mensaje": "Derecho desactivado"}


# ── Indicadores ────────────────────────────────

@router.get("/indicadores", response_model=List[IndicadorResponse])
def listar_indicadores(
    derecho_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    return catalogo_service.listar_indicadores(db, derecho_id)


@router.post("/indicadores", response_model=IndicadorResponse)
def crear_indicador(
    data: IndicadorCreate,
    db: Session = Depends(get_db),
    _: dict = Depends(require_role("director", "coordinador")),
):
    return catalogo_service.crear_indicador(db, data.model_dump())


@router.put("/indicadores/{ind_id}", response_model=IndicadorResponse)
def actualizar_indicador(
    ind_id: int,
    data: IndicadorUpdate,
    db: Session = Depends(get_db),
    _: dict = Depends(require_role("director", "coordinador")),
):
    return catalogo_service.actualizar_indicador(db, ind_id, data.model_dump(exclude_unset=True))


@router.delete("/indicadores/{ind_id}")
def eliminar_indicador(
    ind_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(require_role("director", "coordinador")),
):
    catalogo_service.eliminar_indicador(db, ind_id)
    return {"mensaje": "Indicador desactivado"}
