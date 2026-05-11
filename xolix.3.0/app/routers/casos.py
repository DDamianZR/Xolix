from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_current_user
from app.schemas.caso import CasoCreate, CasoUpdate, NotaCreate, ParticipanteCreate, HechoVictimalCreate
from app.services import caso_service

router = APIRouter(prefix="/api/casos", tags=["Casos"])


# ── CRUD Caso ──────────────────────────────

@router.post("/")
def crear_caso(
    data: CasoCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    creador_id = current_user.get("user_id")
    hecho_data = data.hecho_victimal.model_dump() if data.hecho_victimal else None
    caso = caso_service.crear_caso(
        db, data.titulo, data.descripcion, data.estado, data.nivel_riesgo,
        creador_id, hecho_data, data.participante_ids,
    )
    return {"mensaje": "Caso creado correctamente", "id": caso.id, "folio": caso.folio}


@router.get("/")
def listar_casos(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user.get("user_id")
    return caso_service.listar_casos(db, user_id)


@router.get("/{caso_id}")
def obtener_caso(
    caso_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user.get("user_id")
    return caso_service.obtener_caso(db, caso_id, user_id)


@router.put("/{caso_id}")
def actualizar_caso(
    caso_id: int,
    data: CasoUpdate,
    db: Session = Depends(get_db),
    _current_user: dict = Depends(get_current_user),
):
    caso_service.actualizar_caso(db, caso_id, data.titulo, data.descripcion, data.estado, data.nivel_riesgo)
    return {"mensaje": "Caso actualizado correctamente"}


@router.delete("/{caso_id}")
def eliminar_caso(
    caso_id: int,
    db: Session = Depends(get_db),
    _current_user: dict = Depends(get_current_user),
):
    caso_service.eliminar_caso(db, caso_id)
    return {"mensaje": "Caso eliminado correctamente"}


# ── Hecho Victimal ─────────────────────────

@router.put("/{caso_id}/hecho-victimal")
def actualizar_hecho(
    caso_id: int,
    data: HechoVictimalCreate,
    db: Session = Depends(get_db),
    _current_user: dict = Depends(get_current_user),
):
    caso_service.actualizar_hecho_victimal(db, caso_id, data.model_dump())
    return {"mensaje": "Hecho victimal actualizado"}


# ── Notas ──────────────────────────────────

@router.post("/{caso_id}/notas")
def crear_nota(
    caso_id: int,
    data: NotaCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    autor_id = current_user.get("user_id")
    nota = caso_service.crear_nota(db, caso_id, autor_id, data.area, data.contenido, data.privada, data.etiquetas)
    return {"mensaje": "Nota creada", "id": nota.id}


@router.put("/notas/{nota_id}")
def editar_nota(
    nota_id: int,
    data: NotaCreate,
    db: Session = Depends(get_db),
    _current_user: dict = Depends(get_current_user),
):
    caso_service.editar_nota(db, nota_id, data.contenido)
    return {"mensaje": "Nota actualizada"}


# ── Documentos ─────────────────────────────

@router.post("/{caso_id}/documentos")
def subir_documento(
    caso_id: int,
    nombre: str = Form(...),
    categoria: str = Form("otro"),
    archivo: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user.get("user_id")
    doc = caso_service.subir_documento(db, caso_id, user_id, nombre, archivo, categoria)
    return {"mensaje": "Documento subido", "id": doc.id}


# ── Participantes ──────────────────────────

@router.post("/{caso_id}/participantes")
def agregar_participante(
    caso_id: int,
    data: ParticipanteCreate,
    db: Session = Depends(get_db),
    _current_user: dict = Depends(get_current_user),
):
    p = caso_service.agregar_participante(db, caso_id, data.usuario_id, data.area, data.permiso)
    return {"mensaje": "Participante agregado", "id": p.id}


@router.delete("/{caso_id}/participantes/{usuario_id}")
def remover_participante(
    caso_id: int,
    usuario_id: int,
    db: Session = Depends(get_db),
    _current_user: dict = Depends(get_current_user),
):
    caso_service.remover_participante(db, caso_id, usuario_id)
    return {"mensaje": "Participante removido"}
