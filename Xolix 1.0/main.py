from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models
import schemas
import crud
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi import HTTPException
from security import create_access_token

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Proyecto Xolix")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def root():
    return FileResponse("static/registro.html")
@app.get("/login")
def login_page():
    return FileResponse("static/login.html")




app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/usuarios/")
def crear_usuario(user: schemas.UserCreate, db: Session = Depends(get_db)):
    nuevo_usuario = crud.crear_usuario(db, user)
    
    if not nuevo_usuario:
        raise HTTPException(
            status_code=400,
            detail="El correo ya está registrado"
        )

    return {
        "mensaje": "Usuario creado correctamente",
        "id": nuevo_usuario.id
    }

@app.get("/usuarios/")
def listar_usuarios(db: Session = Depends(get_db)):
    usuarios = crud.obtener_usuarios(db)
    return usuarios


@app.post("/login/")
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    usuario = crud.autenticar_usuario(db, user.correo, user.password)

    if not usuario:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")

    token = create_access_token({"sub": usuario.correo})

    return {
        "access_token": token,
        "token_type": "bearer"
    }

