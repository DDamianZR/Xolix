from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_current_user
from app.schemas.proceso import ProcesoCreate, ProcesoUpdate, SubtareaCreate
from app.services import proceso_service

router = APIRouter(prefix="/api/procesos", tags=["Procesos"])


@router.post("/")
def crear_proceso(
    data: ProcesoCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    creador_id = current_user.get("user_id")
    proceso = proceso_service.crear_proceso(
        db,
        data.titulo,
        data.descripcion,
        data.expediente_id,
        creador_id,
        data.usuario_ids,
        data.prioridad,
        data.fecha_vencimiento,
    )
    return {"mensaje": "Proceso creado correctamente", "id": proceso.id}


@router.get("/")
def listar_procesos(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user.get("user_id")
    return proceso_service.obtener_procesos_usuario(db, user_id)


@router.get("/{proceso_id}")
def obtener_proceso(
    proceso_id: int,
    db: Session = Depends(get_db),
    _current_user: dict = Depends(get_current_user),
):
    proceso = proceso_service.obtener_proceso(db, proceso_id)
    if not proceso:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Proceso no encontrado")
    return proceso


@router.put("/{proceso_id}")
def actualizar_proceso(
    proceso_id: int,
    data: ProcesoUpdate,
    db: Session = Depends(get_db),
    _current_user: dict = Depends(get_current_user),
):
    proceso_service.actualizar_proceso(
        db,
        proceso_id,
        data.titulo,
        data.descripcion,
        data.estado,
        data.expediente_id,
        data.prioridad,
        data.fecha_vencimiento,
    )
    return {"mensaje": "Proceso actualizado correctamente"}


@router.post("/{proceso_id}/subtareas")
def agregar_subtarea(
    proceso_id: int,
    data: SubtareaCreate,
    db: Session = Depends(get_db),
    _current_user: dict = Depends(get_current_user),
):
    subtarea = proceso_service.agregar_subtarea(db, proceso_id, data.titulo, data.fecha_vencimiento)
    return {"mensaje": "Subtarea agregada", "id": subtarea.id}


@router.patch("/subtareas/{subtarea_id}/toggle")
def toggle_subtarea(
    subtarea_id: int,
    db: Session = Depends(get_db),
    _current_user: dict = Depends(get_current_user),
):
    subtarea = proceso_service.toggle_subtarea(db, subtarea_id)
    return {"completada": subtarea.completada}


@router.delete("/{proceso_id}")
def eliminar_proceso(
    proceso_id: int,
    db: Session = Depends(get_db),
    _current_user: dict = Depends(get_current_user),
):
    proceso_service.eliminar_proceso(db, proceso_id)
    return {"mensaje": "Proceso eliminado correctamente"}
