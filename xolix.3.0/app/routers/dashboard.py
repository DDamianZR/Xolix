from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.dependencies import get_db, get_current_user
from app.models.user import User
from app.models.proceso import Proceso, EstadoProceso
from app.models.expediente import Expediente
from app.models.extras import AuditLog

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])

@router.get("/stats")
def get_dashboard_stats(
    db: Session = Depends(get_db),
    _current_user: dict = Depends(get_current_user),
):
    total_usuarios = db.query(func.count(User.id)).scalar()
    usuarios_activos = db.query(func.count(User.id)).filter(User.activo == True).scalar()
    
    procesos_pendientes = db.query(func.count(Proceso.id)).filter(Proceso.estado != EstadoProceso.terminado).scalar()
    expedientes_totales = db.query(func.count(Expediente.id)).scalar()
    
    # Recent activity from AuditLog
    recent_activity = (
        db.query(AuditLog)
        .join(User, AuditLog.usuario_id == User.id)
        .order_by(AuditLog.fecha.desc())
        .limit(10)
        .all()
    )
    
    activity_list = [
        {
            "id": log.id,
            "usuario": f"{log.usuario.nombre} {log.usuario.apellido_paterno}",
            "accion": log.accion,
            "detalle": log.detalle,
            "fecha": log.fecha
        }
        for log in recent_activity
    ]
    
    return {
        "usuarios": {
            "total": total_usuarios,
            "activos": usuarios_activos
        },
        "procesos": {
            "pendientes": procesos_pendientes
        },
        "expedientes": {
            "total": expedientes_totales
        },
        "actividad": activity_list
    }
