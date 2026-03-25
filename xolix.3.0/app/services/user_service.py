from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from datetime import date

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.security import hash_password, verify_password


def calcular_edad(fecha_nacimiento: date) -> int:
    today = date.today()
    return today.year - fecha_nacimiento.year - (
        (today.month, today.day) < (fecha_nacimiento.month, fecha_nacimiento.day)
    )


def crear_usuario(db: Session, user: UserCreate) -> User:
    user_dict = user.model_dump()

    # Cross-validate CURP with fecha_nacimiento
    from app.validators.mexican_ids import validar_curp_fecha, validar_curp_sexo

    ok, msg = validar_curp_fecha(user.curp, user.fecha_nacimiento)
    if not ok:
        raise HTTPException(status_code=400, detail=msg)

    ok, msg = validar_curp_sexo(user.curp, user.sexo)
    if not ok:
        raise HTTPException(status_code=400, detail=msg)

    # Calcular edad
    edad = calcular_edad(user.fecha_nacimiento)
    if edad < 18:
        raise HTTPException(status_code=400, detail="El usuario debe ser mayor de 18 años")

    user_dict["edad"] = edad
    user_dict["password"] = hash_password(user_dict["password"])
    user_dict["activo"] = True

    nuevo_usuario = User(**user_dict)
    db.add(nuevo_usuario)

    try:
        db.commit()
        db.refresh(nuevo_usuario)
        return nuevo_usuario
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="El correo ya está registrado")


def obtener_usuarios(db: Session) -> list[User]:
    return db.query(User).all()


def obtener_usuario_por_id(db: Session, usuario_id: int) -> User | None:
    return db.query(User).filter(User.id == usuario_id).first()


def actualizar_usuario(db: Session, usuario_id: int, user: UserUpdate) -> User:
    usuario = db.query(User).filter(User.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    datos = user.model_dump(exclude_unset=True)

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

    try:
        db.commit()
        db.refresh(usuario)
        return usuario
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="El correo ya está registrado")


def cambiar_estado_usuario(db: Session, usuario_id: int, activo: bool) -> User:
    usuario = db.query(User).filter(User.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    usuario.activo = activo
    db.commit()
    db.refresh(usuario)
    return usuario


def eliminar_usuario(db: Session, usuario_id: int) -> bool:
    usuario = db.query(User).filter(User.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    db.delete(usuario)
    db.commit()
    return True


def autenticar_usuario(db: Session, correo: str, password: str) -> User | None:
    usuario = db.query(User).filter(User.correo == correo).first()

    if not usuario:
        return None

    if not usuario.activo:
        return None

    if not verify_password(password, usuario.password):
        return None

    return usuario
