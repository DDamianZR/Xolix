import os
import shutil
from sqlalchemy.orm import Session
from fastapi import HTTPException, UploadFile

from app.models.expediente import Expediente, ExpedienteCompartido, PermisoExpediente
from app.models.user import User
from app.config import get_settings

settings = get_settings()
UPLOAD_DIR = settings.upload_dir


def _ensure_upload_dir():
    os.makedirs(UPLOAD_DIR, exist_ok=True)


def crear_expediente(db: Session, nombre: str, descripcion: str | None, archivo: UploadFile, propietario_id: int) -> Expediente:
    _ensure_upload_dir()

    # Save file
    ext = os.path.splitext(archivo.filename or "file")[1] or ".pdf"
    safe_name = f"exp_{propietario_id}_{nombre.replace(' ', '_')}{ext}"
    file_path = os.path.join(UPLOAD_DIR, safe_name)

    with open(file_path, "wb") as f:
        shutil.copyfileobj(archivo.file, f)

    expediente = Expediente(
        nombre=nombre,
        descripcion=descripcion,
        archivo_path=file_path,
        tipo_archivo=ext.lstrip("."),
        propietario_id=propietario_id,
    )
    db.add(expediente)
    db.commit()
    db.refresh(expediente)
    return expediente


def obtener_expedientes_propios(db: Session, usuario_id: int) -> list[Expediente]:
    return db.query(Expediente).filter(Expediente.propietario_id == usuario_id).all()


def obtener_expedientes_compartidos(db: Session, usuario_id: int) -> list[dict]:
    compartidos = (
        db.query(ExpedienteCompartido)
        .filter(ExpedienteCompartido.usuario_id == usuario_id)
        .all()
    )
    result = []
    for c in compartidos:
        exp = db.query(Expediente).filter(Expediente.id == c.expediente_id).first()
        if exp:
            result.append({
                "expediente": exp,
                "permiso": c.permiso.value,
            })
    return result


def obtener_expediente(db: Session, expediente_id: int) -> Expediente | None:
    return db.query(Expediente).filter(Expediente.id == expediente_id).first()


def compartir_expediente(db: Session, expediente_id: int, correo_destino: str, permiso: str, propietario_id: int):
    # Verify ownership
    exp = db.query(Expediente).filter(Expediente.id == expediente_id).first()
    if not exp:
        raise HTTPException(status_code=404, detail="Expediente no encontrado")
    if exp.propietario_id != propietario_id:
        raise HTTPException(status_code=403, detail="Solo el propietario puede compartir este expediente")

    # Find target user
    usuario_destino = db.query(User).filter(User.correo == correo_destino).first()
    if not usuario_destino:
        raise HTTPException(status_code=404, detail="Usuario destino no encontrado")

    if usuario_destino.id == propietario_id:
        raise HTTPException(status_code=400, detail="No puedes compartir un expediente contigo mismo")

    # Check if already shared
    existing = (
        db.query(ExpedienteCompartido)
        .filter(
            ExpedienteCompartido.expediente_id == expediente_id,
            ExpedienteCompartido.usuario_id == usuario_destino.id,
        )
        .first()
    )
    if existing:
        existing.permiso = PermisoExpediente(permiso)
        db.commit()
        return existing

    compartido = ExpedienteCompartido(
        expediente_id=expediente_id,
        usuario_id=usuario_destino.id,
        permiso=PermisoExpediente(permiso),
    )
    db.add(compartido)
    db.commit()
    db.refresh(compartido)
    return compartido


def eliminar_expediente(db: Session, expediente_id: int, usuario_id: int):
    exp = db.query(Expediente).filter(Expediente.id == expediente_id).first()
    if not exp:
        raise HTTPException(status_code=404, detail="Expediente no encontrado")
    if exp.propietario_id != usuario_id:
        raise HTTPException(status_code=403, detail="Solo el propietario puede eliminar este expediente")

    # Remove file
    if os.path.exists(exp.archivo_path):
        os.remove(exp.archivo_path)

    db.delete(exp)
    db.commit()
    return True
