from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import models
import schemas
from security import hash_password, verify_password
from datetime import date


# ==============================
# UTILIDADES
# ==============================

def calcular_edad(fecha_nacimiento: date):
    today = date.today()
    return today.year - fecha_nacimiento.year - (
        (today.month, today.day) < (fecha_nacimiento.month, fecha_nacimiento.day)
    )


# ==============================
# CREAR USUARIO
# ==============================

def crear_usuario(db: Session, user: schemas.UserCreate):
    user_dict = user.dict()

    # Calcular edad
    edad = calcular_edad(user.fecha_nacimiento)
    if edad < 18:
        return None  # Puedes lanzar excepción si prefieres

    user_dict["edad"] = edad
    user_dict["password"] = hash_password(user_dict["password"])
    user_dict["activo"] = True  # Por defecto usuario activo

    nuevo_usuario = models.User(**user_dict)
    db.add(nuevo_usuario)

    try:
        db.commit()
        db.refresh(nuevo_usuario)
        return nuevo_usuario
    except IntegrityError:
        db.rollback()
        return None


# ==============================
# OBTENER USUARIOS
# ==============================

def obtener_usuarios(db: Session):
    return db.query(models.User).all()


def obtener_usuario_por_id(db: Session, usuario_id: int):
    return db.query(models.User).filter(models.User.id == usuario_id).first()


# ==============================
# ACTUALIZAR USUARIO
# ==============================

def actualizar_usuario(db: Session, usuario_id: int, user: schemas.UserUpdate):
    usuario = db.query(models.User).filter(models.User.id == usuario_id).first()
    if not usuario:
        return None

    datos = user.dict(exclude_unset=True)

    # Recalcular edad si cambia fecha
    if "fecha_nacimiento" in datos:
        datos["edad"] = calcular_edad(datos["fecha_nacimiento"])

    # Manejo de password
    if "password" in datos:
        if datos["password"]:
            datos["password"] = hash_password(datos["password"])
        else:
            del datos["password"]

    for campo, valor in datos.items():
        setattr(usuario, campo, valor)

    db.commit()
    db.refresh(usuario)
    return usuario


# ==============================
# CAMBIAR ESTADO (ACTIVAR / DESACTIVAR)
# ==============================

def cambiar_estado_usuario(db: Session, usuario_id: int, activo: bool):
    usuario = db.query(models.User).filter(models.User.id == usuario_id).first()
    if not usuario:
        return None

    usuario.activo = activo
    db.commit()
    db.refresh(usuario)
    return usuario


# ==============================
# ELIMINAR USUARIO
# ==============================

def eliminar_usuario(db: Session, usuario_id: int):
    usuario = db.query(models.User).filter(models.User.id == usuario_id).first()
    if not usuario:
        return None

    db.delete(usuario)
    db.commit()
    return True


# ==============================
# AUTENTICACIÓN SEGURA
# ==============================

def autenticar_usuario(db: Session, correo: str, password: str):
    usuario = db.query(models.User).filter(models.User.correo == correo).first()

    # No revelar si el usuario existe o está inactivo
    if not usuario:
        return None

    # 🔐 Validar que esté activo
    if not usuario.activo:
        return None

    # 🔐 Validar contraseña
    if not verify_password(password, usuario.password):
        return None

    return usuario