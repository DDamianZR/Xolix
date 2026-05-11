from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
import sys

from app.config import get_settings
from app.database import engine, Base

# Import ALL models to ensure they are registered
from app.models.user import User  # noqa: F401
from app.models.expediente import Expediente, ExpedienteCompartido  # noqa: F401
from app.models.proceso import Proceso, Subtarea  # noqa: F401
from app.models.caso import Caso, HechoVictimal, CasoParticipante, NotaCaso, DocumentoCaso  # noqa: F401

from app.routers import auth, users, sepomex, expedientes, procesos, casos

settings = get_settings()

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Proyecto Xolix",
    description="Sistema de Gestión de Personal",
    version="3.0.0",
)

# CORS — allow React dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    print(f"422 ERROR DETECTED ON {request.url.path}: {exc.errors()}", file=sys.stderr)
    return JSONResponse(status_code=422, content={"detail": exc.errors()})

# Mount routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(sepomex.router)
app.include_router(expedientes.router)
app.include_router(procesos.router)
app.include_router(casos.router)


@app.get("/api/health")
def health_check():
    return {"status": "ok", "version": "3.0.0"}


