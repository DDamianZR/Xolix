import json
import os
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func as sql_func
from fastapi import HTTPException, UploadFile

from app.models.caso import (
    Caso, HechoVictimal, CasoParticipante, NotaCaso, DocumentoCaso,
    EstadoCaso, NivelRiesgo, AreaProfesional, PermisoCaso, TipoViolencia, CategoriaDocumento,
)
from app.models.user import User
from app.config import get_settings


# ── Folio Generator ────────────────────────

def _generar_folio(db: Session) -> str:
    anio = datetime.now().year
    count = db.query(sql_func.count(Caso.id)).scalar() or 0
    return f"XOL-{anio}-{str(count + 1).zfill(3)}"


# ── CRUD Caso ──────────────────────────────

def crear_caso(
    db: Session,
    titulo: str,
    descripcion: str | None,
    estado: str,
    nivel_riesgo: str,
    creador_id: int,
    hecho_victimal_data: dict | None = None,
    participantes_data: list[dict] | None = None,
) -> Caso:
    folio = _generar_folio(db)

    caso = Caso(
        folio=folio,
        titulo=titulo,
        descripcion=descripcion,
        estado=EstadoCaso(estado) if estado else EstadoCaso.activo,
        nivel_riesgo=NivelRiesgo(nivel_riesgo) if nivel_riesgo else NivelRiesgo.medio,
        creador_id=creador_id,
    )
    db.add(caso)
    db.flush()

    # Create hecho victimal if data provided
    if hecho_victimal_data:
        tv = hecho_victimal_data.get("tipo_violencia")
        hecho = HechoVictimal(
            caso_id=caso.id,
            victima_nombres=hecho_victimal_data.get("victima_nombres"),
            victima_apellido_paterno=hecho_victimal_data.get("victima_apellido_paterno"),
            victima_apellido_materno=hecho_victimal_data.get("victima_apellido_materno"),
            victima_curp=hecho_victimal_data.get("victima_curp"),
            menor_nombres=hecho_victimal_data.get("menor_nombres"),
            menor_apellido_paterno=hecho_victimal_data.get("menor_apellido_paterno"),
            menor_apellido_materno=hecho_victimal_data.get("menor_apellido_materno"),
            menor_curp=hecho_victimal_data.get("menor_curp"),
            edad_menor=hecho_victimal_data.get("edad_menor"),
            fecha_incidente=hecho_victimal_data.get("fecha_incidente"),
            ubicacion=hecho_victimal_data.get("ubicacion"),
            descripcion_delito=hecho_victimal_data.get("descripcion_delito"),
            tipo_violencia=TipoViolencia(tv) if tv else None,
            referencia_juridica=hecho_victimal_data.get("referencia_juridica"),
            referencia_fud=hecho_victimal_data.get("referencia_fud"),
            consideraciones=hecho_victimal_data.get("consideraciones"),
        )
        db.add(hecho)

    # Add creator as admin participant
    db.add(CasoParticipante(
        caso_id=caso.id,
        usuario_id=creador_id,
        area=AreaProfesional.general,
        permiso=PermisoCaso.admin_caso,
    ))

    # Add other participants
    if participantes_data:
        for p in participantes_data:
            uid = p.get("usuario_id")
            if uid and uid != creador_id:
                db.add(CasoParticipante(
                    caso_id=caso.id,
                    usuario_id=uid,
                    area=AreaProfesional(p.get("area", "general")),
                    permiso=PermisoCaso(p.get("permiso", "escritura")),
                ))

    db.commit()
    db.refresh(caso)
    return caso


def listar_casos(db: Session, usuario_id: int) -> list[dict]:
    """List cases where user is a participant."""
    casos = (
        db.query(Caso)
        .filter(Caso.participantes.any(CasoParticipante.usuario_id == usuario_id))
        .order_by(
            # urgente first, then activo, seguimiento, cerrado
            Caso.estado.asc(),
            Caso.fecha_creacion.desc(),
        )
        .all()
    )
    return [_caso_to_list(c) for c in casos]


def obtener_caso(db: Session, caso_id: int, usuario_id: int) -> dict:
    caso = db.query(Caso).filter(Caso.id == caso_id).first()
    if not caso:
        raise HTTPException(status_code=404, detail="Caso no encontrado")

    # Find user's participant record to determine area
    participante = (
        db.query(CasoParticipante)
        .filter(CasoParticipante.caso_id == caso_id, CasoParticipante.usuario_id == usuario_id)
        .first()
    )
    user_area = participante.area.value if participante else None
    is_admin = participante and participante.permiso == PermisoCaso.admin_caso

    return _caso_to_detail(caso, user_area, is_admin)


def actualizar_caso(db: Session, caso_id: int, titulo: str | None, descripcion: str | None, estado: str | None, nivel_riesgo: str | None) -> Caso:
    caso = db.query(Caso).filter(Caso.id == caso_id).first()
    if not caso:
        raise HTTPException(status_code=404, detail="Caso no encontrado")
    if titulo is not None:
        caso.titulo = titulo
    if descripcion is not None:
        caso.descripcion = descripcion
    if estado is not None:
        caso.estado = EstadoCaso(estado)
    if nivel_riesgo is not None:
        caso.nivel_riesgo = NivelRiesgo(nivel_riesgo)
    db.commit()
    db.refresh(caso)
    return caso


def eliminar_caso(db: Session, caso_id: int):
    caso = db.query(Caso).filter(Caso.id == caso_id).first()
    if not caso:
        raise HTTPException(status_code=404, detail="Caso no encontrado")
    db.delete(caso)
    db.commit()
    return True


# ── Hecho Victimal ─────────────────────────

def actualizar_hecho_victimal(db: Session, caso_id: int, data: dict) -> HechoVictimal:
    hecho = db.query(HechoVictimal).filter(HechoVictimal.caso_id == caso_id).first()
    if not hecho:
        tv = data.get("tipo_violencia")
        hecho = HechoVictimal(
            caso_id=caso_id,
            tipo_violencia=TipoViolencia(tv) if tv else None,
        )
        db.add(hecho)

    for field in ["victima_nombres", "victima_apellido_paterno", "victima_apellido_materno", "victima_curp",
                  "menor_nombres", "menor_apellido_paterno", "menor_apellido_materno", "menor_curp",
                  "edad_menor", "fecha_incidente", "ubicacion", "descripcion_delito",
                  "referencia_juridica", "referencia_fud", "consideraciones"]:
        if field in data and data[field] is not None:
            setattr(hecho, field, data[field])

    if "tipo_violencia" in data and data["tipo_violencia"]:
        hecho.tipo_violencia = TipoViolencia(data["tipo_violencia"])

    db.commit()
    db.refresh(hecho)
    return hecho


# ── Notas ──────────────────────────────────

def crear_nota(db: Session, caso_id: int, autor_id: int, area: str, contenido: str, privada: bool, etiquetas: list[str]) -> NotaCaso:
    nota = NotaCaso(
        caso_id=caso_id,
        autor_id=autor_id,
        area=AreaProfesional(area) if area else AreaProfesional.general,
        contenido=contenido,
        privada=privada,
        etiquetas=json.dumps(etiquetas) if etiquetas else None,
    )
    db.add(nota)
    db.commit()
    db.refresh(nota)
    return nota


def editar_nota(db: Session, nota_id: int, contenido: str) -> NotaCaso:
    nota = db.query(NotaCaso).filter(NotaCaso.id == nota_id).first()
    if not nota:
        raise HTTPException(status_code=404, detail="Nota no encontrada")
    nota.contenido = contenido
    db.commit()
    db.refresh(nota)
    return nota


# ── Documentos ─────────────────────────────

def subir_documento(
    db: Session, caso_id: int, subido_por_id: int,
    nombre: str, archivo: UploadFile, categoria: str,
) -> DocumentoCaso:
    settings = get_settings()
    caso_dir = os.path.join(settings.upload_dir, "casos", str(caso_id))
    os.makedirs(caso_dir, exist_ok=True)

    ext = os.path.splitext(archivo.filename)[1] if archivo.filename else ".pdf"
    safe_name = f"{nombre.replace(' ', '_')}_{int(datetime.now().timestamp())}{ext}"
    file_path = os.path.join(caso_dir, safe_name)

    with open(file_path, "wb") as f:
        content = archivo.file.read()
        f.write(content)

    tipo = ext.replace(".", "").lower() if ext else "pdf"

    doc = DocumentoCaso(
        caso_id=caso_id,
        subido_por_id=subido_por_id,
        nombre=nombre,
        archivo_path=file_path,
        tipo_archivo=tipo,
        categoria=CategoriaDocumento(categoria) if categoria else CategoriaDocumento.otro,
        version=1,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


# ── Participantes ──────────────────────────

def agregar_participante(db: Session, caso_id: int, usuario_id: int, area: str, permiso: str = "escritura") -> CasoParticipante:
    existing = db.query(CasoParticipante).filter(
        CasoParticipante.caso_id == caso_id,
        CasoParticipante.usuario_id == usuario_id,
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="El usuario ya es participante de este caso")

    p = CasoParticipante(
        caso_id=caso_id,
        usuario_id=usuario_id,
        area=AreaProfesional(area),
        permiso=PermisoCaso(permiso),
    )
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


def remover_participante(db: Session, caso_id: int, usuario_id: int):
    p = db.query(CasoParticipante).filter(
        CasoParticipante.caso_id == caso_id,
        CasoParticipante.usuario_id == usuario_id,
    ).first()
    if not p:
        raise HTTPException(status_code=404, detail="Participante no encontrado")
    db.delete(p)
    db.commit()
    return True


# ── Serializers ────────────────────────────

def _caso_to_list(caso: Caso) -> dict:
    return {
        "id": caso.id,
        "folio": caso.folio,
        "titulo": caso.titulo,
        "estado": caso.estado.value,
        "nivel_riesgo": caso.nivel_riesgo.value,
        "fecha_creacion": caso.fecha_creacion,
        "participantes_count": len(caso.participantes),
        "notas_count": len(caso.notas),
        "documentos_count": len(caso.documentos),
    }


def _caso_to_detail(caso: Caso, user_area: str | None, is_admin: bool) -> dict:
    # Filter notes: admins and general area see all shared; specialists see their area + shared
    notas_visibles = []
    for n in caso.notas:
        if is_admin or user_area == "general":
            # Admins see all non-private notes, plus their own private ones
            if not n.privada or n.autor_id:
                notas_visibles.append(n)
        else:
            # Specialists see: their own notes + shared notes + same-area private notes
            if not n.privada:
                notas_visibles.append(n)
            elif n.area.value == user_area:
                notas_visibles.append(n)

    return {
        "id": caso.id,
        "folio": caso.folio,
        "titulo": caso.titulo,
        "descripcion": caso.descripcion,
        "estado": caso.estado.value,
        "nivel_riesgo": caso.nivel_riesgo.value,
        "creador_id": caso.creador_id,
        "fecha_creacion": caso.fecha_creacion,
        "hecho_victimal": _hecho_to_dict(caso.hecho_victimal) if caso.hecho_victimal else None,
        "participantes": [
            {
                "id": p.id,
                "usuario_id": p.usuario_id,
                "usuario_nombre": f"{p.usuario.nombre} {p.usuario.apellido_paterno}" if p.usuario else None,
                "area": p.area.value,
                "permiso": p.permiso.value,
            }
            for p in caso.participantes
        ],
        "notas": [
            {
                "id": n.id,
                "caso_id": n.caso_id,
                "autor_id": n.autor_id,
                "autor_nombre": f"{n.autor.nombre} {n.autor.apellido_paterno}" if n.autor else None,
                "autor_area": n.area.value,
                "area": n.area.value,
                "contenido": n.contenido,
                "privada": n.privada,
                "etiquetas": json.loads(n.etiquetas) if n.etiquetas else [],
                "fecha_creacion": n.fecha_creacion,
                "fecha_actualizacion": n.fecha_actualizacion,
            }
            for n in notas_visibles
        ],
        "documentos": [
            {
                "id": d.id,
                "nombre": d.nombre,
                "tipo_archivo": d.tipo_archivo,
                "categoria": d.categoria.value,
                "version": d.version,
                "subido_por_nombre": f"{d.subido_por.nombre} {d.subido_por.apellido_paterno}" if d.subido_por else None,
                "fecha_subida": d.fecha_subida,
            }
            for d in caso.documentos
        ],
    }


def _hecho_to_dict(h: HechoVictimal) -> dict:
    return {
        "id": h.id,
        "victima_nombres": h.victima_nombres,
        "victima_apellido_paterno": h.victima_apellido_paterno,
        "victima_apellido_materno": h.victima_apellido_materno,
        "victima_curp": h.victima_curp,
        "menor_nombres": h.menor_nombres,
        "menor_apellido_paterno": h.menor_apellido_paterno,
        "menor_apellido_materno": h.menor_apellido_materno,
        "menor_curp": h.menor_curp,
        "edad_menor": h.edad_menor,
        "fecha_incidente": h.fecha_incidente,
        "ubicacion": h.ubicacion,
        "descripcion_delito": h.descripcion_delito,
        "tipo_violencia": h.tipo_violencia.value if h.tipo_violencia else None,
        "referencia_juridica": h.referencia_juridica,
        "referencia_fud": h.referencia_fud,
        "fecha_creacion_expediente": h.fecha_creacion_expediente,
        "consideraciones": h.consideraciones,
    }
