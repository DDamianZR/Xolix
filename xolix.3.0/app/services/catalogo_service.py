from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.catalogo import Derecho, Indicador, CategoriaDerecho


def listar_derechos(db: Session, activos_only: bool = True):
    q = db.query(Derecho)
    if activos_only:
        q = q.filter(Derecho.activo == True)
    return q.order_by(Derecho.categoria, Derecho.nombre).all()


def obtener_derecho(db: Session, derecho_id: int) -> Derecho:
    d = db.query(Derecho).filter(Derecho.id == derecho_id).first()
    if not d:
        raise HTTPException(status_code=404, detail="Derecho no encontrado")
    return d


def crear_derecho(db: Session, data: dict) -> Derecho:
    categoria = data.get("categoria", "proteccion")
    try:
        categoria_enum = CategoriaDerecho(categoria)
    except ValueError:
        categoria_enum = CategoriaDerecho.otro
    d = Derecho(
        nombre=data["nombre"],
        descripcion=data.get("descripcion"),
        categoria=categoria_enum,
        articulo_referencia=data.get("articulo_referencia"),
    )
    db.add(d)
    db.commit()
    db.refresh(d)
    return d


def actualizar_derecho(db: Session, derecho_id: int, data: dict) -> Derecho:
    d = obtener_derecho(db, derecho_id)
    for k, v in data.items():
        if v is not None:
            if k == "categoria":
                try:
                    v = CategoriaDerecho(v)
                except ValueError:
                    v = CategoriaDerecho.otro
            setattr(d, k, v)
    db.commit()
    db.refresh(d)
    return d


def eliminar_derecho(db: Session, derecho_id: int):
    d = obtener_derecho(db, derecho_id)
    d.activo = False
    db.commit()


def listar_indicadores(db: Session, derecho_id: int = None):
    q = db.query(Indicador).filter(Indicador.activo == True)
    if derecho_id:
        q = q.filter(Indicador.derecho_id == derecho_id)
    return q.order_by(Indicador.derecho_id, Indicador.nombre).all()


def crear_indicador(db: Session, data: dict) -> Indicador:
    obtener_derecho(db, data["derecho_id"])
    ind = Indicador(
        derecho_id=data["derecho_id"],
        nombre=data["nombre"],
        descripcion=data.get("descripcion"),
        tipo_evaluacion=data.get("tipo_evaluacion", "si_no"),
    )
    db.add(ind)
    db.commit()
    db.refresh(ind)
    return ind


def actualizar_indicador(db: Session, ind_id: int, data: dict) -> Indicador:
    ind = db.query(Indicador).filter(Indicador.id == ind_id).first()
    if not ind:
        raise HTTPException(status_code=404, detail="Indicador no encontrado")
    for k, v in data.items():
        if v is not None:
            setattr(ind, k, v)
    db.commit()
    db.refresh(ind)
    return ind


def eliminar_indicador(db: Session, ind_id: int):
    ind = db.query(Indicador).filter(Indicador.id == ind_id).first()
    if not ind:
        raise HTTPException(status_code=404, detail="Indicador no encontrado")
    ind.activo = False
    db.commit()
