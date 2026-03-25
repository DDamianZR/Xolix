from sqlalchemy.orm import Session
from fastapi import Depends
from app.database import SessionLocal
from app.security import verify_token


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(token: dict = Depends(verify_token)) -> dict:
    """Returns the decoded JWT payload for the current authenticated user."""
    return token


def require_role(*roles: str):
    """Dependency factory that checks if the current user has one of the required roles."""
    def check_role(current_user: dict = Depends(get_current_user)) -> dict:
        user_role = current_user.get("rol", "")
        if user_role not in roles:
            from fastapi import HTTPException
            raise HTTPException(
                status_code=403,
                detail="No tienes permisos para realizar esta acción"
            )
        return current_user
    return check_role
