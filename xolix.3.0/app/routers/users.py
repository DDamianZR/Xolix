from fastapi import APIRouter, Depends, Query, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
import os
import shutil

from app.dependencies import get_db, get_current_user, require_role
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.services import user_service
from app.config import get_settings

router = APIRouter(prefix="/api/usuarios", tags=["Usuarios"])


@router.get("/", response_model=list[UserResponse])
def listar_usuarios(
    db: Session = Depends(get_db),
    _current_user: dict = Depends(get_current_user),
):
    return user_service.obtener_usuarios(db)


@router.get("/{usuario_id}", response_model=UserResponse)
def obtener_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    _current_user: dict = Depends(get_current_user),
):
    usuario = user_service.obtener_usuario_por_id(db, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario


@router.post("/", response_model=dict)
def crear_usuario(
    user: UserCreate,
    db: Session = Depends(get_db),
    _admin: dict = Depends(require_role("director", "coordinador")),
):
    nuevo = user_service.crear_usuario(db, user)
    return {"mensaje": "Usuario creado correctamente", "id": nuevo.id}


@router.put("/{usuario_id}", response_model=dict)
def actualizar_usuario(
    usuario_id: int,
    user: UserUpdate,
    db: Session = Depends(get_db),
    _admin: dict = Depends(require_role("director", "coordinador")),
):
    user_service.actualizar_usuario(db, usuario_id, user)
    return {"mensaje": "Usuario actualizado correctamente"}


@router.patch("/{usuario_id}/acceso", response_model=dict)
def cambiar_acceso(
    usuario_id: int,
    activo: bool = Query(...),
    db: Session = Depends(get_db),
    _admin: dict = Depends(require_role("director", "coordinador")),
):
    user_service.cambiar_estado_usuario(db, usuario_id, activo)
    estado = "activado" if activo else "desactivado"
    return {"mensaje": f"Usuario {estado} correctamente"}


@router.delete("/{usuario_id}", response_model=dict)
def eliminar_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    _admin: dict = Depends(require_role("director", "coordinador")),
):
    user_service.eliminar_usuario(db, usuario_id)
    return {"mensaje": "Usuario eliminado correctamente"}


@router.post("/{usuario_id}/foto", response_model=dict)
def subir_foto_perfil(
    usuario_id: int,
    foto: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Sube una foto de perfil para el usuario."""
    # Validar tipo de archivo
    allowed = {".jpg", ".jpeg", ".png", ".webp"}
    ext = os.path.splitext(foto.filename or "file")[1].lower()
    if ext not in allowed:
        raise HTTPException(status_code=400, detail="Solo se permiten imágenes (jpg, png, webp)")

    # Validar tamaño (máx 5MB)
    foto.file.seek(0, 2)
    size = foto.file.tell()
    foto.file.seek(0)
    if size > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="La imagen no debe superar 5 MB")

    settings = get_settings()
    upload_dir = os.path.join(settings.upload_dir, "fotos")
    os.makedirs(upload_dir, exist_ok=True)

    filename = f"user_{usuario_id}{ext}"
    filepath = os.path.join(upload_dir, filename)

    with open(filepath, "wb") as f:
        shutil.copyfileobj(foto.file, f)

    # Update user record
    usuario = user_service.obtener_usuario_por_id(db, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    usuario.foto_perfil = filepath
    db.commit()

    return {"mensaje": "Foto actualizada correctamente", "path": filepath}

