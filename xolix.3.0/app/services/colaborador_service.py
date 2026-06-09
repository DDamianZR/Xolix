from sqlalchemy.orm import Session
from sqlalchemy import or_
from fastapi import HTTPException
from datetime import date, timedelta

from app.models.user import User
from app.models.equipo import EvaluacionConfianza
from app.services.extras_service import registrar_audit


def listar_colaboradores(db: Session, tipo: str = None, confianza_min: int = None,
                         confianza_max: int = None, rol: str = None) -> list[User]:
    q = db.query(User).filter(User.activo == True)
    if tipo:
        q = q.filter(User.tipo_colaboracion == tipo)
    if confianza_min:
        q = q.filter(User.nivel_confianza >= confianza_min)
    if confianza_max:
        q = q.filter(User.nivel_confianza <= confianza_max)
    if rol:
        q = q.filter(User.rol == rol)
    return q.order_by(User.nivel_confianza.desc(), User.nombre).all()


def colaboradores_pendientes_revision(db: Session, meses: int = 6) -> list[User]:
    limite = date.today() - timedelta(days=meses * 30)
    return db.query(User).filter(
        User.activo == True,
        or_(
            User.fecha_ultima_evaluacion == None,
            User.fecha_ultima_evaluacion < limite,
        ),
    ).order_by(User.fecha_ultima_evaluacion.asc().nullsfirst()).all()


def evaluar_confianza(db: Session, usuario_id: int, evaluador_id: int,
                      nivel_nuevo: int, justificacion: str, actor_rol: str) -> EvaluacionConfianza:
    if actor_rol not in ("director", "coordinador", "trabajador_social"):
        raise HTTPException(403, "Solo director, coordinador o trabajador social pueden evaluar")
    if not (1 <= nivel_nuevo <= 5):
        raise HTTPException(400, "El nivel de confianza debe estar entre 1 y 5")
    if not justificacion or len(justificacion.strip()) < 10:
        raise HTTPException(400, "La justificación debe tener al menos 10 caracteres")

    usuario = db.query(User).filter(User.id == usuario_id).first()
    if not usuario:
        raise HTTPException(404, "Usuario no encontrado")
    if usuario_id == evaluador_id:
        raise HTTPException(400, "No puedes evaluarte a ti mismo")

    nivel_anterior = usuario.nivel_confianza or 3
    eval_obj = EvaluacionConfianza(
        usuario_id=usuario_id, evaluador_id=evaluador_id,
        nivel_anterior=nivel_anterior, nivel_nuevo=nivel_nuevo,
        justificacion=justificacion.strip(),
    )
    db.add(eval_obj)

    usuario.nivel_confianza = nivel_nuevo
    usuario.fecha_ultima_evaluacion = date.today()
    db.commit()
    db.refresh(eval_obj)

    registrar_audit(db, evaluador_id, "confianza_evaluar",
                    f"usuario_id={usuario_id} {nivel_anterior}→{nivel_nuevo}")
    return eval_obj


def historial_confianza(db: Session, usuario_id: int) -> list[EvaluacionConfianza]:
    if not db.query(User).filter(User.id == usuario_id).first():
        raise HTTPException(404, "Usuario no encontrado")
    return db.query(EvaluacionConfianza).filter(
        EvaluacionConfianza.usuario_id == usuario_id,
    ).order_by(EvaluacionConfianza.fecha.desc()).all()
