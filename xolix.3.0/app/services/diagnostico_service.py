from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import date as date_type

from app.services.extras_service import registrar_audit
from app.models.diagnostico import (
    Diagnostico, EvidenciaDiagnostico, IndicadorDiagnostico, DerechoVulnerado,
    TipoDiagnostico, SeveridadVulneracion
)
from app.models.catalogo import Indicador, Derecho


def obtener_diagnostico(db: Session, diag_id: int) -> Diagnostico:
    d = db.query(Diagnostico).filter(Diagnostico.id == diag_id).first()
    if not d:
        raise HTTPException(status_code=404, detail="Diagnóstico no encontrado")
    return d


def listar_diagnosticos(db: Session, caso_nna_id: int):
    return db.query(Diagnostico).filter(
        Diagnostico.caso_nna_id == caso_nna_id
    ).order_by(Diagnostico.fecha.desc()).all()


def crear_diagnostico(db: Session, data: dict, responsable_id: int) -> Diagnostico:
    try:
        tipo_enum = TipoDiagnostico(data["tipo"])
    except ValueError:
        raise HTTPException(status_code=422, detail=f"Tipo de diagnóstico inválido: {data['tipo']}")

    diag = Diagnostico(
        caso_nna_id=data["caso_nna_id"],
        tipo=tipo_enum,
        fecha=data["fecha"],
        responsable_id=responsable_id,
        observaciones=data.get("observaciones"),
    )
    db.add(diag)
    db.flush()

    indicadores_data = data.get("indicadores", [])
    derechos_vulnerados_ids = set()

    for ind_data in indicadores_data:
        ind_eval = IndicadorDiagnostico(
            diagnostico_id=diag.id,
            indicador_id=ind_data["indicador_id"],
            valor=ind_data.get("valor"),
            observacion=ind_data.get("observacion"),
            vulnerado=ind_data.get("vulnerado", False),
        )
        db.add(ind_eval)

        if ind_data.get("vulnerado"):
            indicador = db.query(Indicador).filter(Indicador.id == ind_data["indicador_id"]).first()
            if indicador:
                derechos_vulnerados_ids.add(indicador.derecho_id)

    for derecho_id in derechos_vulnerados_ids:
        dv = DerechoVulnerado(
            diagnostico_id=diag.id,
            derecho_id=derecho_id,
            severidad=SeveridadVulneracion.moderada,
            generado_automaticamente=True,
        )
        db.add(dv)

    db.commit()
    db.refresh(diag)
    registrar_audit(db, responsable_id, "CREATE_DIAGNOSTICO", "diagnostico", diag.id)
    return diag


def actualizar_diagnostico(db: Session, diag_id: int, data: dict) -> Diagnostico:
    diag = obtener_diagnostico(db, diag_id)
    for k, v in data.items():
        if v is not None:
            setattr(diag, k, v)
    db.commit()
    db.refresh(diag)
    return diag


def agregar_evidencia(db: Session, diag_id: int, data: dict, archivo_path: str = None) -> EvidenciaDiagnostico:
    obtener_diagnostico(db, diag_id)
    ev = EvidenciaDiagnostico(
        diagnostico_id=diag_id,
        nombre=data["nombre"],
        descripcion=data.get("descripcion"),
        tipo_archivo=data.get("tipo_archivo"),
        archivo_path=archivo_path,
    )
    db.add(ev)
    db.commit()
    db.refresh(ev)
    return ev


def agregar_derecho_vulnerado(db: Session, diag_id: int, data: dict) -> DerechoVulnerado:
    obtener_diagnostico(db, diag_id)
    try:
        sev = SeveridadVulneracion(data.get("severidad", "moderada"))
    except ValueError:
        sev = SeveridadVulneracion.moderada
    dv = DerechoVulnerado(
        diagnostico_id=diag_id,
        derecho_id=data["derecho_id"],
        severidad=sev,
        recomendacion=data.get("recomendacion"),
        generado_automaticamente=False,
    )
    db.add(dv)
    db.commit()
    db.refresh(dv)
    return dv


def eliminar_diagnostico(db: Session, diag_id: int):
    diag = obtener_diagnostico(db, diag_id)
    db.delete(diag)
    db.commit()


def resumen_derechos_vulnerados(db: Session, caso_nna_id: int):
    diags = db.query(Diagnostico).filter(Diagnostico.caso_nna_id == caso_nna_id).all()
    derechos_map = {}
    for diag in diags:
        for dv in diag.derechos_vulnerados:
            d_id = dv.derecho_id
            if d_id not in derechos_map:
                derecho = db.query(Derecho).filter(Derecho.id == d_id).first()
                derechos_map[d_id] = {
                    "derecho_id": d_id,
                    "nombre": derecho.nombre if derecho else str(d_id),
                    "categoria": derecho.categoria if derecho else None,
                    "severidad_maxima": dv.severidad,
                    "cantidad_ocurrencias": 1,
                    "recomendaciones": [dv.recomendacion] if dv.recomendacion else [],
                }
            else:
                derechos_map[d_id]["cantidad_ocurrencias"] += 1
                if dv.recomendacion:
                    derechos_map[d_id]["recomendaciones"].append(dv.recomendacion)
    return list(derechos_map.values())
