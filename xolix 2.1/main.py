from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models
import schemas
import crud
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from security import create_access_token, verify_token

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Proyecto Xolix")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ── Páginas ──────────────────────────────────────────────
@app.get("/")
def root():
    return FileResponse("static/login.html")

@app.get("/registro")
def registro_page():
    return FileResponse("static/registro.html")

@app.get("/dashboard")
def dashboard_page():
    return FileResponse("static/dashboard.html")

@app.get("/usuario/{id}")
def detalle_page(id: int):
    return FileResponse("static/detalle.html")

@app.get("/editar/{id}")
def editar_page(id: int):
    return FileResponse("static/editar.html")

# ── Auth ─────────────────────────────────────────────────
@app.post("/login/")
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    usuario = crud.autenticar_usuario(db, user.correo, user.password)
    if not usuario:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    token = create_access_token({"sub": usuario.correo, "rol": usuario.rol})
    return {"access_token": token, "token_type": "bearer", "rol": usuario.rol}

# ── Usuarios ─────────────────────────────────────────────
@app.get("/usuarios/")
def listar_usuarios(db: Session = Depends(get_db), token: dict = Depends(verify_token)):
    return crud.obtener_usuarios(db)

@app.get("/usuarios/{usuario_id}")
def obtener_usuario(usuario_id: int, db: Session = Depends(get_db), token: dict = Depends(verify_token)):
    usuario = crud.obtener_usuario_por_id(db, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario

@app.post("/usuarios/")
def crear_usuario(user: schemas.UserCreate, db: Session = Depends(get_db), token: dict = Depends(verify_token)):
    rol_token = token.get("rol", "")
    if rol_token not in ["director", "coordinador"]:
        raise HTTPException(status_code=403, detail="Solo el director o coordinador pueden registrar personal")
    nuevo = crud.crear_usuario(db, user)
    if not nuevo:
        raise HTTPException(status_code=400, detail="El correo ya está registrado")
    return {"mensaje": "Usuario creado correctamente", "id": nuevo.id}

@app.put("/usuarios/{usuario_id}")
def actualizar_usuario(usuario_id: int, user: schemas.UserUpdate, db: Session = Depends(get_db), token: dict = Depends(verify_token)):
    rol_token = token.get("rol", "")
    if rol_token not in ["director", "coordinador"]:
        raise HTTPException(status_code=403, detail="Sin permisos para modificar usuarios")
    actualizado = crud.actualizar_usuario(db, usuario_id, user)
    if not actualizado:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return {"mensaje": "Usuario actualizado correctamente"}

@app.patch("/usuarios/{usuario_id}/acceso")
def cambiar_acceso(usuario_id: int, activo: bool, db: Session = Depends(get_db), token: dict = Depends(verify_token)):
    rol_token = token.get("rol", "")
    if rol_token not in ["director", "coordinador"]:
        raise HTTPException(status_code=403, detail="Sin permisos")
    resultado = crud.cambiar_estado_usuario(db, usuario_id, activo)
    if not resultado:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    estado = "activado" if activo else "desactivado"
    return {"mensaje": f"Usuario {estado} correctamente"}

@app.delete("/usuarios/{usuario_id}")
def eliminar_usuario(usuario_id: int, db: Session = Depends(get_db), token: dict = Depends(verify_token)):
    rol_token = token.get("rol", "")
    if rol_token not in ["director", "coordinador"]:
        raise HTTPException(status_code=403, detail="Sin permisos para eliminar usuarios")
    resultado = crud.eliminar_usuario(db, usuario_id)
    if not resultado:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return {"mensaje": "Usuario eliminado correctamente"}
