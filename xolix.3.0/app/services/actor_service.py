from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.actor import Actor, ResponsableActor, HorarioActor, ServicioActor, RequisitoServicio, TipoActor


def listar_actores(db: Session, municipio: str = None, estado: str = None,
                   derecho_id: int = None, tipo: str = None,
                   es_gratuito: bool = None, activos_only: bool = True):
    q = db.query(Actor)
    if activos_only:
        q = q.filter(Actor.activo == True)
    if municipio:
        q = q.filter(Actor.municipio.ilike(f"%{municipio}%"))
    if estado:
        q = q.filter(Actor.estado.ilike(f"%{estado}%"))
    if tipo:
        q = q.filter(Actor.tipo == tipo)
    if derecho_id is not None or es_gratuito is not None:
        q = q.join(ServicioActor, ServicioActor.actor_id == Actor.id, isouter=True)
        if derecho_id is not None:
            q = q.filter(ServicioActor.derecho_id == derecho_id)
        if es_gratuito is not None:
            q = q.filter(ServicioActor.es_gratuito == es_gratuito)
        q = q.distinct()
    return q.order_by(Actor.nombre).all()


def obtener_actor(db: Session, actor_id: int) -> Actor:
    a = db.query(Actor).filter(Actor.id == actor_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Actor no encontrado")
    return a


def crear_actor(db: Session, data: dict) -> Actor:
    try:
        tipo_enum = TipoActor(data["tipo"])
    except ValueError:
        raise HTTPException(status_code=422, detail=f"Tipo de actor inválido: {data['tipo']}")

    actor = Actor(
        nombre=data["nombre"],
        tipo=tipo_enum,
        descripcion=data.get("descripcion"),
        direccion=data.get("direccion"),
        municipio=data.get("municipio"),
        estado=data.get("estado"),
        pais=data.get("pais", "México"),
        telefono=data.get("telefono"),
        correo=data.get("correo"),
        sitio_web=data.get("sitio_web"),
        redes_sociales=data.get("redes_sociales"),
    )
    db.add(actor)
    db.flush()

    for r in data.get("responsables", []):
        db.add(ResponsableActor(actor_id=actor.id, **r))

    for h in data.get("horarios", []):
        db.add(HorarioActor(actor_id=actor.id, **{k: v for k, v in h.items() if k != "requisitos"}))

    for s in data.get("servicios", []):
        requisitos = s.pop("requisitos", [])
        servicio = ServicioActor(actor_id=actor.id, **s)
        db.add(servicio)
        db.flush()
        for req in requisitos:
            db.add(RequisitoServicio(servicio_id=servicio.id, **req))

    db.commit()
    db.refresh(actor)
    return actor


def actualizar_actor(db: Session, actor_id: int, data: dict) -> Actor:
    actor = obtener_actor(db, actor_id)
    for k, v in data.items():
        if v is not None:
            if k == "tipo":
                try:
                    v = TipoActor(v)
                except ValueError:
                    continue
            setattr(actor, k, v)
    db.commit()
    db.refresh(actor)
    return actor


def eliminar_actor(db: Session, actor_id: int):
    actor = obtener_actor(db, actor_id)
    actor.activo = False
    db.commit()


def agregar_responsable(db: Session, actor_id: int, data: dict) -> ResponsableActor:
    obtener_actor(db, actor_id)
    r = ResponsableActor(actor_id=actor_id, **data)
    db.add(r)
    db.commit()
    db.refresh(r)
    return r


def agregar_servicio(db: Session, actor_id: int, data: dict) -> ServicioActor:
    obtener_actor(db, actor_id)
    requisitos = data.pop("requisitos", [])
    s = ServicioActor(actor_id=actor_id, **data)
    db.add(s)
    db.flush()
    for req in requisitos:
        db.add(RequisitoServicio(servicio_id=s.id, **req))
    db.commit()
    db.refresh(s)
    return s


def eliminar_servicio(db: Session, servicio_id: int):
    s = db.query(ServicioActor).filter(ServicioActor.id == servicio_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")
    s.activo = False
    db.commit()
