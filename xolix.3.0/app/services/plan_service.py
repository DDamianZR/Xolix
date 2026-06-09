from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.services.extras_service import registrar_audit
from app.models.plan import (
    PlanRestitucion, MedidaRestitucion, SeguimientoMedida,
    EstadoPlan, EstadoMedida, TipoMedida
)


def obtener_plan(db: Session, plan_id: int) -> PlanRestitucion:
    p = db.query(PlanRestitucion).filter(PlanRestitucion.id == plan_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Plan no encontrado")
    return p


def listar_planes(db: Session, caso_nna_id: int):
    return db.query(PlanRestitucion).filter(
        PlanRestitucion.caso_nna_id == caso_nna_id
    ).order_by(PlanRestitucion.fecha_creacion.desc()).all()


def crear_plan(db: Session, data: dict, responsable_id: int) -> PlanRestitucion:
    medidas_data = data.pop("medidas", [])
    plan = PlanRestitucion(
        caso_nna_id=data["caso_nna_id"],
        objetivo=data["objetivo"],
        derechos_afectados=data.get("derechos_afectados"),
        responsable_id=data.get("responsable_id") or responsable_id,
        fecha_inicio=data.get("fecha_inicio"),
        fecha_termino=data.get("fecha_termino"),
        observaciones=data.get("observaciones"),
    )
    db.add(plan)
    db.flush()

    for m_data in medidas_data:
        try:
            tipo_enum = TipoMedida(m_data.get("tipo", "otra"))
        except ValueError:
            tipo_enum = TipoMedida.otra
        medida = MedidaRestitucion(
            plan_id=plan.id,
            tipo=tipo_enum,
            descripcion=m_data["descripcion"],
            responsable_id=m_data.get("responsable_id"),
            actor_id=m_data.get("actor_id"),
            recursos_requeridos=m_data.get("recursos_requeridos"),
            fecha_inicio=m_data.get("fecha_inicio"),
            fecha_limite=m_data.get("fecha_limite"),
        )
        db.add(medida)

    db.commit()
    db.refresh(plan)
    registrar_audit(db, responsable_id, "CREATE_PLAN", "plan_restitucion", plan.id)
    return plan


def actualizar_plan(db: Session, plan_id: int, data: dict) -> PlanRestitucion:
    plan = obtener_plan(db, plan_id)
    for k, v in data.items():
        if v is not None:
            if k == "estado":
                try:
                    v = EstadoPlan(v)
                except ValueError:
                    continue
            setattr(plan, k, v)
    db.commit()
    db.refresh(plan)
    return plan


def eliminar_plan(db: Session, plan_id: int):
    plan = obtener_plan(db, plan_id)
    db.delete(plan)
    db.commit()


def obtener_medida(db: Session, medida_id: int) -> MedidaRestitucion:
    m = db.query(MedidaRestitucion).filter(MedidaRestitucion.id == medida_id).first()
    if not m:
        raise HTTPException(status_code=404, detail="Medida no encontrada")
    return m


def agregar_medida(db: Session, plan_id: int, data: dict) -> MedidaRestitucion:
    obtener_plan(db, plan_id)
    try:
        tipo_enum = TipoMedida(data.get("tipo", "otra"))
    except ValueError:
        tipo_enum = TipoMedida.otra
    m = MedidaRestitucion(
        plan_id=plan_id,
        tipo=tipo_enum,
        descripcion=data["descripcion"],
        responsable_id=data.get("responsable_id"),
        actor_id=data.get("actor_id"),
        recursos_requeridos=data.get("recursos_requeridos"),
        fecha_inicio=data.get("fecha_inicio"),
        fecha_limite=data.get("fecha_limite"),
    )
    db.add(m)
    db.commit()
    db.refresh(m)
    return m


def actualizar_medida(db: Session, medida_id: int, data: dict) -> MedidaRestitucion:
    m = obtener_medida(db, medida_id)
    for k, v in data.items():
        if v is not None:
            if k == "estado":
                try:
                    v = EstadoMedida(v)
                except ValueError:
                    continue
            elif k == "tipo":
                try:
                    v = TipoMedida(v)
                except ValueError:
                    continue
            setattr(m, k, v)
    db.commit()
    db.refresh(m)
    return m


def registrar_seguimiento(db: Session, medida_id: int, data: dict, registrado_por_id: int) -> SeguimientoMedida:
    medida = obtener_medida(db, medida_id)
    s = SeguimientoMedida(
        medida_id=medida_id,
        registrado_por_id=registrado_por_id,
        fecha_seguimiento=data["fecha_seguimiento"],
        descripcion_avance=data["descripcion_avance"],
        porcentaje_cumplimiento=data.get("porcentaje_cumplimiento", 0),
        observaciones=data.get("observaciones"),
        evidencias=data.get("evidencias"),
    )
    db.add(s)
    medida.porcentaje_avance = data.get("porcentaje_cumplimiento", medida.porcentaje_avance)
    db.commit()
    db.refresh(s)
    return s
