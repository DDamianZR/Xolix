from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.equipo import EquipoCaso
from app.models.nna import CasoNNA
from app.models.user import User
from app.services.extras_service import registrar_audit

ROLES_VALIDOS = {"psicologo", "trabajador_social", "legal", "medico", "voluntario_apoyo", "coordinador", "otro"}


def _get_caso_o_404(db: Session, caso_id: int) -> CasoNNA:
    caso = db.query(CasoNNA).filter(CasoNNA.id == caso_id).first()
    if not caso:
        raise HTTPException(404, "Caso no encontrado")
    return caso


def _verificar_es_responsable(caso: CasoNNA, user_id: int, rol: str):
    if rol in ("director", "coordinador"):
        return
    if caso.responsable_id != user_id:
        raise HTTPException(403, "Solo el trabajador social responsable puede gestionar el equipo")


def asignar_responsable(db: Session, caso_id: int, ts_id: int, actor_id: int, actor_rol: str) -> CasoNNA:
    if actor_rol not in ("director", "coordinador"):
        raise HTTPException(403, "Solo director o coordinador pueden asignar responsables")
    caso = _get_caso_o_404(db, caso_id)
    ts = db.query(User).filter(User.id == ts_id).first()
    if not ts:
        raise HTTPException(404, "Usuario no encontrado")
    if ts.rol != "trabajador_social":
        raise HTTPException(400, "El responsable debe ser un trabajador social")
    caso.responsable_id = ts_id
    db.commit()
    db.refresh(caso)
    registrar_audit(db, actor_id, "responsable_caso_asignar",
                    f"caso_id={caso_id} responsable_id={ts_id}")
    return caso


def agregar_miembro(db: Session, caso_id: int, usuario_id: int, rol_en_equipo: str,
                    asignado_por_id: int, actor_rol: str, observaciones: str = None) -> EquipoCaso:
    if rol_en_equipo not in ROLES_VALIDOS:
        raise HTTPException(400, f"rol_en_equipo debe ser uno de: {ROLES_VALIDOS}")
    caso = _get_caso_o_404(db, caso_id)
    _verificar_es_responsable(caso, asignado_por_id, actor_rol)

    usuario = db.query(User).filter(User.id == usuario_id).first()
    if not usuario or not usuario.activo:
        raise HTTPException(404, "Usuario no encontrado o inactivo")

    # Si ya existe (inactivo), reactivar
    existente = db.query(EquipoCaso).filter(
        EquipoCaso.caso_id == caso_id,
        EquipoCaso.usuario_id == usuario_id,
    ).first()
    if existente:
        if existente.activo:
            raise HTTPException(400, "El usuario ya es miembro activo del equipo")
        existente.activo = True
        existente.rol_en_equipo = rol_en_equipo
        existente.asignado_por_id = asignado_por_id
        existente.observaciones = observaciones
        db.commit()
        db.refresh(existente)
        registrar_audit(db, asignado_por_id, "equipo_caso_agregar",
                        f"caso_id={caso_id} usuario_id={usuario_id} rol={rol_en_equipo}")
        return existente

    miembro = EquipoCaso(
        caso_id=caso_id, usuario_id=usuario_id, rol_en_equipo=rol_en_equipo,
        asignado_por_id=asignado_por_id, observaciones=observaciones, activo=True,
    )
    db.add(miembro)
    db.commit()
    db.refresh(miembro)
    registrar_audit(db, asignado_por_id, "equipo_caso_agregar",
                    f"caso_id={caso_id} usuario_id={usuario_id} rol={rol_en_equipo}")
    return miembro


def quitar_miembro(db: Session, caso_id: int, usuario_id: int,
                   actor_id: int, actor_rol: str) -> bool:
    caso = _get_caso_o_404(db, caso_id)
    _verificar_es_responsable(caso, actor_id, actor_rol)
    if caso.responsable_id == usuario_id:
        raise HTTPException(400, "No puedes quitar al responsable del equipo")
    miembro = db.query(EquipoCaso).filter(
        EquipoCaso.caso_id == caso_id,
        EquipoCaso.usuario_id == usuario_id,
        EquipoCaso.activo == True,
    ).first()
    if not miembro:
        raise HTTPException(404, "El usuario no es miembro activo del equipo")
    miembro.activo = False
    db.commit()
    registrar_audit(db, actor_id, "equipo_caso_quitar",
                    f"caso_id={caso_id} usuario_id={usuario_id}")
    return True


def cambiar_rol_miembro(db: Session, caso_id: int, usuario_id: int, nuevo_rol: str,
                        actor_id: int, actor_rol: str) -> EquipoCaso:
    if nuevo_rol not in ROLES_VALIDOS:
        raise HTTPException(400, f"rol_en_equipo debe ser uno de: {ROLES_VALIDOS}")
    caso = _get_caso_o_404(db, caso_id)
    _verificar_es_responsable(caso, actor_id, actor_rol)
    miembro = db.query(EquipoCaso).filter(
        EquipoCaso.caso_id == caso_id,
        EquipoCaso.usuario_id == usuario_id,
        EquipoCaso.activo == True,
    ).first()
    if not miembro:
        raise HTTPException(404, "El usuario no es miembro activo del equipo")
    rol_anterior = miembro.rol_en_equipo
    miembro.rol_en_equipo = nuevo_rol
    db.commit()
    db.refresh(miembro)
    registrar_audit(db, actor_id, "equipo_caso_cambio_rol",
                    f"caso_id={caso_id} usuario_id={usuario_id} {rol_anterior}→{nuevo_rol}")
    return miembro


def listar_equipo(db: Session, caso_id: int) -> list[EquipoCaso]:
    _get_caso_o_404(db, caso_id)
    return db.query(EquipoCaso).filter(
        EquipoCaso.caso_id == caso_id,
        EquipoCaso.activo == True,
    ).all()
