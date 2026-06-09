from sqlalchemy.orm import Session
from app.models.extras import AuditLog, Notificacion


def registrar_audit(db: Session, usuario_id: int, accion: str, entidad: str,
                    entidad_id: int = None, detalles: dict = None):
    log = AuditLog(
        usuario_id=usuario_id,
        accion=accion,
        entidad=entidad,
        entidad_id=entidad_id,
        detalles=detalles,
    )
    db.add(log)
    db.commit()
    return log


def listar_audit(db: Session, entidad: str = None, usuario_id: int = None, limit: int = 200):
    q = db.query(AuditLog)
    if entidad:
        q = q.filter(AuditLog.entidad == entidad)
    if usuario_id:
        q = q.filter(AuditLog.usuario_id == usuario_id)
    return q.order_by(AuditLog.fecha.desc()).limit(limit).all()


def crear_notificacion(db: Session, usuario_id: int, mensaje: str, tipo: str = "info"):
    notificacion = Notificacion(usuario_id=usuario_id, mensaje=mensaje, tipo=tipo)
    db.add(notificacion)
    db.commit()
    return notificacion


def obtener_notificaciones(db: Session, usuario_id: int, solo_no_leidas: bool = True):
    query = db.query(Notificacion).filter(Notificacion.usuario_id == usuario_id)
    if solo_no_leidas:
        query = query.filter(Notificacion.leida == False)
    return query.order_by(Notificacion.fecha.desc()).all()


def marcar_leida(db: Session, notificacion_id: int):
    n = db.query(Notificacion).filter(Notificacion.id == notificacion_id).first()
    if n:
        n.leida = True
        db.commit()
    return n
