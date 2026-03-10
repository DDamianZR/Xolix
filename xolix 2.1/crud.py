from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import models
import schemas
from security import hash_password, verify_password


def crear_usuario(db: Session, user: schemas.UserCreate):
    user_dict = user.dict()
    user_dict["password"] = hash_password(user_dict["password"])
    nuevo_usuario = models.User(**user_dict)
    db.add(nuevo_usuario)
    try:
        db.commit()
        db.refresh(nuevo_usuario)
        return nuevo_usuario
    except IntegrityError:
        db.rollback()
        return None


def obtener_usuarios(db: Session):
    return db.query(models.User).all()


def obtener_usuario_por_id(db: Session, usuario_id: int):
    return db.query(models.User).filter(models.User.id == usuario_id).first()


def actualizar_usuario(db: Session, usuario_id: int, user: schemas.UserUpdate):
    usuario = db.query(models.User).filter(models.User.id == usuario_id).first()
    if not usuario:
        return None
    datos = user.dict(exclude_unset=True)
    if "password" in datos and datos["password"]:
        datos["password"] = hash_password(datos["password"])
    elif "password" in datos:
        del datos["password"]
    for campo, valor in datos.items():
        setattr(usuario, campo, valor)
    db.commit()
    db.refresh(usuario)
    return usuario


def cambiar_estado_usuario(db: Session, usuario_id: int, activo: bool):
    usuario = db.query(models.User).filter(models.User.id == usuario_id).first()
    if not usuario:
        return None
    usuario.activo = activo
    db.commit()
    return usuario


def eliminar_usuario(db: Session, usuario_id: int):
    usuario = db.query(models.User).filter(models.User.id == usuario_id).first()
    if not usuario:
        return None
    db.delete(usuario)
    db.commit()
    return True


def autenticar_usuario(db: Session, correo: str, password: str):
    usuario = db.query(models.User).filter(models.User.correo == correo).first()
    if not usuario or not verify_password(password, usuario.password):
        return None
    return usuario
