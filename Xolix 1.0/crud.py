from sqlalchemy.orm import Session
import models
import schemas
from security import hash_password

from sqlalchemy.exc import IntegrityError

def crear_usuario(db, user):
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


from security import verify_password

def autenticar_usuario(db, correo: str, password: str):
    usuario = db.query(models.User).filter(models.User.correo == correo).first()
    
    if not usuario:
        return None
    
    if not verify_password(password, usuario.password):
        return None
    
    return usuario
