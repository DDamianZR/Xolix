from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional
import io

from app.dependencies import get_db, get_current_user, require_role
from app.models.nna import CasoNNA
from app.models.actor import Actor
from app.models.diagnostico import Diagnostico, DerechoVulnerado
from app.models.catalogo import Derecho
from app.models.extras import AuditLog
from app.services import export_service
from app.services.extras_service import listar_audit

router = APIRouter(prefix="/api/reportes", tags=["Reportes"])


# ── Indicadores globales ─────────────────────

@router.get("/indicadores")
def indicadores_globales(
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    total_casos = db.query(CasoNNA).count()
    casos_activos = db.query(CasoNNA).filter(CasoNNA.estado == "activo").count()
    casos_cerrados = db.query(CasoNNA).filter(CasoNNA.estado == "cerrado").count()
    total_actores = db.query(Actor).filter(Actor.activo == True).count()
    total_diagnosticos = db.query(Diagnostico).count()

    return {
        "total_casos": total_casos,
        "casos_activos": casos_activos,
        "casos_cerrados": casos_cerrados,
        "total_actores": total_actores,
        "total_diagnosticos": total_diagnosticos,
    }


@router.get("/derechos-vulnerados")
def derechos_vulnerados_frecuencia(
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    """Frecuencia de derechos vulnerados a través de todos los diagnósticos."""
    from sqlalchemy import func
    rows = (
        db.query(DerechoVulnerado.derecho_id, func.count(DerechoVulnerado.id).label("frecuencia"))
        .group_by(DerechoVulnerado.derecho_id)
        .order_by(func.count(DerechoVulnerado.id).desc())
        .all()
    )
    result = []
    for r in rows:
        derecho = db.query(Derecho).filter(Derecho.id == r.derecho_id).first()
        result.append({
            "derecho_id": r.derecho_id,
            "nombre": derecho.nombre if derecho else str(r.derecho_id),
            "categoria": derecho.categoria.value if derecho and hasattr(derecho.categoria, "value") else None,
            "frecuencia": r.frecuencia,
        })
    return result


@router.get("/evolucion-casos")
def evolucion_casos_mensual(
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    """Cantidad de casos creados por mes (últimos 12 meses)."""
    from sqlalchemy import func, extract
    from datetime import datetime, timedelta

    hace_12_meses = datetime.now() - timedelta(days=365)
    rows = (
        db.query(
            extract("year", CasoNNA.fecha_creacion).label("anio"),
            extract("month", CasoNNA.fecha_creacion).label("mes"),
            func.count(CasoNNA.id).label("cantidad"),
        )
        .filter(CasoNNA.fecha_creacion >= hace_12_meses)
        .group_by("anio", "mes")
        .order_by("anio", "mes")
        .all()
    )
    return [{"anio": int(r.anio), "mes": int(r.mes), "cantidad": r.cantidad} for r in rows]


# ── Auditoría ────────────────────────────────

@router.get("/auditoria")
def ver_auditoria(
    entidad: Optional[str] = Query(None),
    usuario_id: Optional[int] = Query(None),
    limit: int = Query(100, le=500),
    db: Session = Depends(get_db),
    _: dict = Depends(require_role("director", "coordinador")),
):
    logs = listar_audit(db, entidad=entidad, usuario_id=usuario_id, limit=limit)
    return [
        {
            "id": l.id,
            "usuario_id": l.usuario_id,
            "accion": l.accion,
            "entidad": l.entidad,
            "entidad_id": l.entidad_id,
            "detalles": l.detalles,
            "fecha": l.fecha,
        }
        for l in logs
    ]


# ── Exportación PDF ──────────────────────────

@router.get("/exportar/casos/pdf")
def exportar_casos_pdf(
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    casos = db.query(CasoNNA).order_by(CasoNNA.fecha_creacion.desc()).all()
    pdf_bytes = export_service.generar_pdf_casos(casos)
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=casos_nna.pdf"},
    )


@router.get("/exportar/diagnostico/{diag_id}/pdf")
def exportar_diagnostico_pdf(
    diag_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    from app.services.diagnostico_service import obtener_diagnostico
    diag = obtener_diagnostico(db, diag_id)
    caso = db.query(CasoNNA).filter(CasoNNA.id == diag.caso_nna_id).first()
    pdf_bytes = export_service.generar_pdf_diagnostico(diag, caso)
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=diagnostico_{diag_id}.pdf"},
    )


# ── Exportación Excel ─────────────────────────

@router.get("/exportar/casos/excel")
def exportar_casos_excel(
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    casos = db.query(CasoNNA).order_by(CasoNNA.fecha_creacion.desc()).all()
    xlsx_bytes = export_service.generar_excel_casos(casos)
    return StreamingResponse(
        io.BytesIO(xlsx_bytes),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=casos_nna.xlsx"},
    )


@router.get("/exportar/actores/excel")
def exportar_actores_excel(
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    actores = db.query(Actor).filter(Actor.activo == True).order_by(Actor.nombre).all()
    xlsx_bytes = export_service.generar_excel_actores(actores)
    return StreamingResponse(
        io.BytesIO(xlsx_bytes),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=actores.xlsx"},
    )
