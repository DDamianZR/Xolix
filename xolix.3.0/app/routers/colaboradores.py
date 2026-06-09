from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.dependencies import get_db, get_current_user, require_role
from app.schemas.equipo import ColaboradorResponse, EvaluacionCreate, EvaluacionResponse
from app.services import colaborador_service

router = APIRouter(prefix="/api/colaboradores", tags=["Colaboradores"])


@router.get("/", response_model=List[ColaboradorResponse])
def listar_colaboradores(
    tipo: Optional[str] = Query(None, description="planta o voluntario"),
    confianza_min: Optional[int] = Query(None, ge=1, le=5),
    confianza_max: Optional[int] = Query(None, ge=1, le=5),
    rol: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role("trabajador_social", "director", "coordinador")),
):
    return colaborador_service.listar_colaboradores(db, tipo, confianza_min, confianza_max, rol)


@router.get("/pendientes-revision", response_model=List[ColaboradorResponse])
def pendientes_revision(
    meses: int = Query(6, ge=1, le=24),
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role("trabajador_social", "director", "coordinador")),
):
    return colaborador_service.colaboradores_pendientes_revision(db, meses)


@router.post("/{usuario_id}/evaluar-confianza", response_model=EvaluacionResponse)
def evaluar_confianza(
    usuario_id: int,
    data: EvaluacionCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role("trabajador_social", "director", "coordinador")),
):
    return colaborador_service.evaluar_confianza(
        db, usuario_id,
        evaluador_id=current_user["user_id"],
        nivel_nuevo=data.nivel_nuevo,
        justificacion=data.justificacion,
        actor_rol=current_user["rol"],
    )


@router.get("/{usuario_id}/historial-confianza", response_model=List[EvaluacionResponse])
def historial_confianza(
    usuario_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role("trabajador_social", "director", "coordinador")),
):
    return colaborador_service.historial_confianza(db, usuario_id)
