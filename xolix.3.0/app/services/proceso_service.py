from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.proceso import Proceso, Subtarea, EstadoProceso, proceso_usuarios
from app.models.user import User


def crear_proceso(db: Session, titulo: str, descripcion: str | None, expediente_id: int | None, creador_id: int, usuario_ids: list[int]) -> Proceso:
    proceso = Proceso(
        titulo=titulo,
        descripcion=descripcion,
        estado=EstadoProceso.pendiente,
        expediente_id=expediente_id,
        creador_id=creador_id,
    )
    db.add(proceso)
    db.flush()

    # Add creator as participant
    all_user_ids = set(usuario_ids)
    all_user_ids.add(creador_id)

    for uid in all_user_ids:
        user = db.query(User).filter(User.id == uid).first()
        if user:
            proceso.usuarios.append(user)

    db.commit()
    db.refresh(proceso)
    return proceso


def obtener_procesos_usuario(db: Session, usuario_id: int) -> list[dict]:
    procesos = (
        db.query(Proceso)
        .filter(Proceso.usuarios.any(User.id == usuario_id))
        .all()
    )
    return [_proceso_con_progreso(p) for p in procesos]


def obtener_proceso(db: Session, proceso_id: int) -> dict | None:
    proceso = db.query(Proceso).filter(Proceso.id == proceso_id).first()
    if not proceso:
        return None
    return _proceso_con_progreso(proceso)


def actualizar_proceso(db: Session, proceso_id: int, titulo: str | None, descripcion: str | None, estado: str | None, expediente_id: int | None) -> Proceso:
    proceso = db.query(Proceso).filter(Proceso.id == proceso_id).first()
    if not proceso:
        raise HTTPException(status_code=404, detail="Proceso no encontrado")

    if titulo is not None:
        proceso.titulo = titulo
    if descripcion is not None:
        proceso.descripcion = descripcion
    if estado is not None:
        proceso.estado = EstadoProceso(estado)
    if expediente_id is not None:
        proceso.expediente_id = expediente_id

    db.commit()
    db.refresh(proceso)
    return proceso


def agregar_subtarea(db: Session, proceso_id: int, titulo: str) -> Subtarea:
    proceso = db.query(Proceso).filter(Proceso.id == proceso_id).first()
    if not proceso:
        raise HTTPException(status_code=404, detail="Proceso no encontrado")

    subtarea = Subtarea(proceso_id=proceso_id, titulo=titulo)
    db.add(subtarea)
    db.commit()
    db.refresh(subtarea)
    return subtarea


def toggle_subtarea(db: Session, subtarea_id: int) -> Subtarea:
    subtarea = db.query(Subtarea).filter(Subtarea.id == subtarea_id).first()
    if not subtarea:
        raise HTTPException(status_code=404, detail="Subtarea no encontrada")

    subtarea.completada = not subtarea.completada

    # Auto-update process state based on subtask progress
    proceso = subtarea.proceso
    subtareas = proceso.subtareas
    if subtareas:
        completadas = sum(1 for s in subtareas if s.completada)
        total = len(subtareas)
        if completadas == total:
            proceso.estado = EstadoProceso.terminado
        elif completadas > 0:
            proceso.estado = EstadoProceso.en_proceso
        else:
            proceso.estado = EstadoProceso.pendiente

    db.commit()
    db.refresh(subtarea)
    return subtarea


def eliminar_proceso(db: Session, proceso_id: int):
    proceso = db.query(Proceso).filter(Proceso.id == proceso_id).first()
    if not proceso:
        raise HTTPException(status_code=404, detail="Proceso no encontrado")
    db.delete(proceso)
    db.commit()
    return True


def _proceso_con_progreso(proceso: Proceso) -> dict:
    """Calculate progress percentage from subtasks."""
    subtareas = proceso.subtareas
    total = len(subtareas)
    completadas = sum(1 for s in subtareas if s.completada) if total else 0
    progreso = (completadas / total * 100) if total > 0 else 0.0

    return {
        "id": proceso.id,
        "titulo": proceso.titulo,
        "descripcion": proceso.descripcion,
        "estado": proceso.estado.value,
        "expediente_id": proceso.expediente_id,
        "expediente_nombre": proceso.expediente.titulo if proceso.expediente else None,
        "creador_id": proceso.creador_id,
        "progreso": round(progreso, 1),
        "usuarios": [
            {"id": u.id, "nombre": u.nombre, "apellido_paterno": u.apellido_paterno}
            for u in proceso.usuarios
        ],
        "subtareas": [
            {"id": s.id, "titulo": s.titulo, "completada": s.completada}
            for s in subtareas
        ],
        "fecha_creacion": proceso.fecha_creacion,
    }
