from fastapi import APIRouter, Depends, UploadFile, File, Form
from typing import List
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_current_user
from app.schemas.diagnostico import (
    DiagnosticoCreate, DiagnosticoUpdate, DiagnosticoResponse,
    DerechoVulneradoCreate, DerechoVulneradoResponse,
)
from app.services import diagnostico_service

router = APIRouter(prefix="/api/diagnosticos", tags=["Diagnósticos"])


@router.get("/caso/{caso_nna_id}", response_model=List[DiagnosticoResponse])
def listar_diagnosticos(
    caso_nna_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    return diagnostico_service.listar_diagnosticos(db, caso_nna_id)


@router.get("/{diag_id}", response_model=DiagnosticoResponse)
def obtener_diagnostico(
    diag_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    return diagnostico_service.obtener_diagnostico(db, diag_id)


@router.post("/", response_model=DiagnosticoResponse)
def crear_diagnostico(
    data: DiagnosticoCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    return diagnostico_service.crear_diagnostico(
        db, data.model_dump(), current_user.get("user_id")
    )


@router.put("/{diag_id}", response_model=DiagnosticoResponse)
def actualizar_diagnostico(
    diag_id: int,
    data: DiagnosticoUpdate,
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    return diagnostico_service.actualizar_diagnostico(db, diag_id, data.model_dump(exclude_unset=True))


@router.delete("/{diag_id}")
def eliminar_diagnostico(
    diag_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    diagnostico_service.eliminar_diagnostico(db, diag_id)
    return {"mensaje": "Diagnóstico eliminado"}


@router.post("/{diag_id}/derechos-vulnerados", response_model=DerechoVulneradoResponse)
def agregar_derecho_vulnerado(
    diag_id: int,
    data: DerechoVulneradoCreate,
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    return diagnostico_service.agregar_derecho_vulnerado(db, diag_id, data.model_dump())


@router.get("/caso/{caso_nna_id}/resumen-derechos")
def resumen_derechos(
    caso_nna_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    return diagnostico_service.resumen_derechos_vulnerados(db, caso_nna_id)
