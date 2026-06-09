from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_current_user
from app.schemas.user import UserLogin, TokenResponse
from app.services.user_service import autenticar_usuario, obtener_usuario_por_id
from app.security import create_access_token
from fastapi import HTTPException

router = APIRouter(prefix="/api/auth", tags=["Autenticación"])


@router.post("/login", response_model=TokenResponse)
def login(user: UserLogin, db: Session = Depends(get_db)):
    usuario = autenticar_usuario(db, user.correo, user.password)
    if not usuario:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    if not usuario.verificado:
        raise HTTPException(status_code=401, detail="Debes verificar tu correo electrónico antes de iniciar sesión.")
    token = create_access_token({"sub": usuario.correo, "rol": usuario.rol, "user_id": usuario.id})
    return TokenResponse(access_token=token, rol=usuario.rol)


@router.get("/me")
def me(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    usuario = obtener_usuario_por_id(db, current_user["user_id"])
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return {"id": usuario.id, "correo": usuario.correo, "rol": usuario.rol,
            "nombre": usuario.nombre, "apellido_paterno": usuario.apellido_paterno}
