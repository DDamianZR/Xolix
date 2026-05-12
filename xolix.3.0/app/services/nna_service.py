from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime

from app.models.nna import (
    CasoNNA, EntrevistaFamilia, PersonaFamiliar, Familiograma, ObservacionNoVerbal,
    HistorialFamiliograma, RelacionFamiliar,
    EstadoCasoNNA, GeneroNNA, TipoSimboloFamiliar, TipoRelacionFamiliar
)
from app.models.user import User
from app.services import proceso_service

# ── CasoNNA ─────────────────────────────────

def crear_caso_nna(db: Session, data: dict, creador_id: int) -> CasoNNA:
    caso = CasoNNA(
        nna_nombre=data.get("nna_nombre"),
        nna_edad=data.get("nna_edad"),
        nna_genero=GeneroNNA(data.get("nna_genero")) if data.get("nna_genero") else None,
        creador_id=creador_id
    )
    db.add(caso)
    db.commit()
    db.refresh(caso)
    return caso

def listar_casos_nna(db: Session, user_id: int, rol: str) -> list[CasoNNA]:
    query = db.query(CasoNNA)
    if rol not in ["director", "coordinador"]:
        query = query.filter(CasoNNA.creador_id == user_id)
    return query.order_by(CasoNNA.fecha_creacion.desc()).all()

def obtener_caso_nna(db: Session, caso_id: int, user_id: int, rol: str) -> CasoNNA:
    caso = db.query(CasoNNA).filter(CasoNNA.id == caso_id).first()
    if not caso:
        raise HTTPException(status_code=404, detail="Caso NNA no encontrado")
    if rol not in ["director", "coordinador"] and caso.creador_id != user_id:
         raise HTTPException(status_code=403, detail="No tienes acceso a este caso")
    return caso

def actualizar_caso_nna(db: Session, caso_id: int, data: dict) -> CasoNNA:
    caso = db.query(CasoNNA).filter(CasoNNA.id == caso_id).first()
    if not caso:
        raise HTTPException(status_code=404, detail="Caso NNA no encontrado")
    if "nna_nombre" in data and data["nna_nombre"] is not None:
        caso.nna_nombre = data["nna_nombre"]
    if "nna_edad" in data:
        caso.nna_edad = data["nna_edad"]
    if "nna_genero" in data and data["nna_genero"]:
        caso.nna_genero = GeneroNNA(data["nna_genero"])
    if "estado" in data and data["estado"]:
        caso.estado = EstadoCasoNNA(data["estado"])
    db.commit()
    db.refresh(caso)
    return caso

def eliminar_caso_nna(db: Session, caso_id: int):
    caso = db.query(CasoNNA).filter(CasoNNA.id == caso_id).first()
    if not caso:
        raise HTTPException(status_code=404, detail="Caso NNA no encontrado")
    db.delete(caso)
    db.commit()

# ── EntrevistaFamilia ────────────────────────

def crear_o_actualizar_entrevista(db: Session, caso_id: int, data: dict) -> EntrevistaFamilia:
    entrevista = db.query(EntrevistaFamilia).filter(EntrevistaFamilia.caso_id == caso_id).first()

    frases = data.get("frases_comunicadas")
    if frases is not None and isinstance(frases, list) and len(frases) > 0 and hasattr(frases[0], "model_dump"):
        frases = [f.model_dump() for f in frases]
    elif frases is None:
        frases = []

    dia_comun = data.get("dia_comun")
    if dia_comun is not None and hasattr(dia_comun, "model_dump"):
        dia_comun = dia_comun.model_dump()

    if not entrevista:
        entrevista = EntrevistaFamilia(
            caso_id=caso_id,
            frases_comunicadas=frases,
            dia_comun=dia_comun,
            grado_negacion=data.get("grado_negacion", 1),
            observaciones_negacion=data.get("observaciones_negacion"),
            completada=data.get("completada", False)
        )
        db.add(entrevista)
    else:
        if "frases_comunicadas" in data:
            entrevista.frases_comunicadas = frases
        if "dia_comun" in data:
            entrevista.dia_comun = dia_comun
        if "grado_negacion" in data:
            entrevista.grado_negacion = data["grado_negacion"]
        if "observaciones_negacion" in data:
            entrevista.observaciones_negacion = data["observaciones_negacion"]
        if "completada" in data:
            entrevista.completada = data["completada"]

    db.commit()
    db.refresh(entrevista)
    return entrevista

def obtener_entrevista(db: Session, caso_id: int) -> EntrevistaFamilia:
    return db.query(EntrevistaFamilia).filter(EntrevistaFamilia.caso_id == caso_id).first()

# ── PersonaFamiliar ──────────────────────────

def crear_persona(db: Session, caso_id: int, data: dict) -> PersonaFamiliar:
    persona = PersonaFamiliar(
        caso_id=caso_id,
        nombre=data.get("nombre"),
        edad=data.get("edad"),
        genero=GeneroNNA(data.get("genero")) if data.get("genero") else None,
        rol_en_familia=data.get("rol_en_familia"),
        tipo_simbolo=TipoSimboloFamiliar(data.get("tipo_simbolo", "normal")),
        observaciones=data.get("observaciones"),
        telefono=data.get("telefono"),
        direccion=data.get("direccion"),
        ocupacion=data.get("ocupacion"),
        escolaridad=data.get("escolaridad"),
        estado_salud=data.get("estado_salud"),
        vive_con_nna=data.get("vive_con_nna", False),
        es_responsable_legal=data.get("es_responsable_legal", False),
    )
    db.add(persona)
    db.commit()
    db.refresh(persona)
    return persona

def listar_personas(db: Session, caso_id: int) -> list[PersonaFamiliar]:
    return db.query(PersonaFamiliar).filter(PersonaFamiliar.caso_id == caso_id).all()

def obtener_persona(db: Session, persona_id: int) -> PersonaFamiliar:
    persona = db.query(PersonaFamiliar).filter(PersonaFamiliar.id == persona_id).first()
    if not persona:
        raise HTTPException(status_code=404, detail="Persona no encontrada")
    return persona

def actualizar_persona(db: Session, persona_id: int, data: dict) -> PersonaFamiliar:
    persona = db.query(PersonaFamiliar).filter(PersonaFamiliar.id == persona_id).first()
    if not persona:
        raise HTTPException(status_code=404, detail="Persona no encontrada")

    campos_str = ["nombre", "rol_en_familia", "observaciones", "telefono", "direccion",
                  "ocupacion", "escolaridad", "estado_salud"]
    for campo in campos_str:
        if campo in data and data[campo] is not None:
            setattr(persona, campo, data[campo])

    if "edad" in data:
        persona.edad = data["edad"]
    if "genero" in data and data["genero"]:
        persona.genero = GeneroNNA(data["genero"])
    if "tipo_simbolo" in data and data["tipo_simbolo"]:
        persona.tipo_simbolo = TipoSimboloFamiliar(data["tipo_simbolo"])
    if "vive_con_nna" in data and data["vive_con_nna"] is not None:
        persona.vive_con_nna = data["vive_con_nna"]
    if "es_responsable_legal" in data and data["es_responsable_legal"] is not None:
        persona.es_responsable_legal = data["es_responsable_legal"]

    db.commit()
    db.refresh(persona)
    return persona

def eliminar_persona(db: Session, persona_id: int):
    persona = db.query(PersonaFamiliar).filter(PersonaFamiliar.id == persona_id).first()
    if not persona:
        raise HTTPException(status_code=404, detail="Persona no encontrada")
    db.delete(persona)
    db.commit()

# ── Familiograma ─────────────────────────────

def upsert_familiograma(db: Session, caso_id: int, grafo_json: dict, imagen_url: str = None,
                         notas_version: str = None, modificado_por_id: int = None) -> Familiograma:
    familiograma = db.query(Familiograma).filter(Familiograma.caso_id == caso_id).first()
    if not familiograma:
        familiograma = Familiograma(caso_id=caso_id, grafo_json=grafo_json, imagen_url=imagen_url)
        db.add(familiograma)
        db.flush()  # Get the id
    else:
        if grafo_json is not None:
            # Guardar versión anterior en historial antes de sobrescribir
            _guardar_en_historial(db, familiograma, modificado_por_id, notas_version)
            familiograma.grafo_json = grafo_json
        if imagen_url is not None:
            familiograma.imagen_url = imagen_url

    db.commit()
    db.refresh(familiograma)
    return familiograma

def _guardar_en_historial(db: Session, familiograma: Familiograma,
                           modificado_por_id: int = None, notas_version: str = None):
    """Snapshot automático del estado previo antes de sobreescribir."""
    if not familiograma.grafo_json:
        return
    # Calcular siguiente número de versión
    ultima = (
        db.query(HistorialFamiliograma)
        .filter(HistorialFamiliograma.familiograma_id == familiograma.id)
        .order_by(HistorialFamiliograma.version.desc())
        .first()
    )
    siguiente_version = (ultima.version + 1) if ultima else 1

    snapshot = HistorialFamiliograma(
        familiograma_id=familiograma.id,
        caso_id=familiograma.caso_id,
        version=siguiente_version,
        grafo_json=familiograma.grafo_json,
        modificado_por_id=modificado_por_id,
        notas_version=notas_version or f"Versión {siguiente_version}"
    )
    db.add(snapshot)

def obtener_familiograma(db: Session, caso_id: int) -> Familiograma:
    return db.query(Familiograma).filter(Familiograma.caso_id == caso_id).first()

def obtener_historial_familiograma(db: Session, caso_id: int) -> list[dict]:
    familiograma = db.query(Familiograma).filter(Familiograma.caso_id == caso_id).first()
    if not familiograma:
        return []
    historial = (
        db.query(HistorialFamiliograma)
        .filter(HistorialFamiliograma.familiograma_id == familiograma.id)
        .order_by(HistorialFamiliograma.version.desc())
        .all()
    )
    result = []
    for h in historial:
        result.append({
            "id": h.id,
            "familiograma_id": h.familiograma_id,
            "caso_id": h.caso_id,
            "version": h.version,
            "grafo_json": h.grafo_json,
            "modificado_por_id": h.modificado_por_id,
            "modificado_por_nombre": (
                f"{h.modificado_por.nombre} {h.modificado_por.apellido_paterno}"
                if h.modificado_por else "Sistema"
            ),
            "notas_version": h.notas_version,
            "fecha": h.fecha,
        })
    return result

def restaurar_version_familiograma(db: Session, caso_id: int, historial_id: int,
                                    modificado_por_id: int) -> Familiograma:
    """Restaura el grafo de una versión del historial."""
    snapshot = db.query(HistorialFamiliograma).filter(
        HistorialFamiliograma.id == historial_id,
        HistorialFamiliograma.caso_id == caso_id
    ).first()
    if not snapshot:
        raise HTTPException(status_code=404, detail="Versión no encontrada")
    return upsert_familiograma(
        db, caso_id, snapshot.grafo_json,
        notas_version=f"Restaurado desde v{snapshot.version}",
        modificado_por_id=modificado_por_id
    )

def exportar_familiograma(db: Session, caso_id: int) -> dict:
    """Exporta datos completos: caso, personas, relaciones y grafo."""
    caso = db.query(CasoNNA).filter(CasoNNA.id == caso_id).first()
    if not caso:
        raise HTTPException(status_code=404, detail="Caso NNA no encontrado")
    personas = db.query(PersonaFamiliar).filter(PersonaFamiliar.caso_id == caso_id).all()
    relaciones = db.query(RelacionFamiliar).filter(RelacionFamiliar.caso_id == caso_id).all()
    familiograma = db.query(Familiograma).filter(Familiograma.caso_id == caso_id).first()

    personas_data = [
        {
            "id": p.id, "nombre": p.nombre, "edad": p.edad,
            "genero": p.genero.value if p.genero else None,
            "rol_en_familia": p.rol_en_familia,
            "tipo_simbolo": p.tipo_simbolo.value if p.tipo_simbolo else "normal",
            "telefono": p.telefono, "direccion": p.direccion,
            "ocupacion": p.ocupacion, "escolaridad": p.escolaridad,
            "estado_salud": p.estado_salud,
            "vive_con_nna": p.vive_con_nna,
            "es_responsable_legal": p.es_responsable_legal,
            "observaciones": p.observaciones,
        } for p in personas
    ]
    relaciones_data = [
        {
            "id": r.id,
            "persona_origen": r.persona_origen.nombre if r.persona_origen else None,
            "persona_destino": r.persona_destino.nombre if r.persona_destino else None,
            "tipo_relacion": r.tipo_relacion.value if r.tipo_relacion else None,
            "descripcion": r.descripcion,
            "bidireccional": r.bidireccional,
        } for r in relaciones
    ]
    return {
        "caso": {
            "id": caso.id,
            "nna_nombre": caso.nna_nombre,
            "nna_edad": caso.nna_edad,
            "nna_genero": caso.nna_genero.value if caso.nna_genero else None,
            "estado": caso.estado.value,
            "fecha_creacion": str(caso.fecha_creacion),
        },
        "personas": personas_data,
        "relaciones": relaciones_data,
        "grafo_json": familiograma.grafo_json if familiograma else None,
        "exportado_en": datetime.now().isoformat(),
    }

# ── RelacionFamiliar ─────────────────────────

def crear_relacion(db: Session, caso_id: int, data: dict) -> RelacionFamiliar:
    # Validar que las personas pertenezcan al caso
    for pid_key in ["persona_origen_id", "persona_destino_id"]:
        p = db.query(PersonaFamiliar).filter(
            PersonaFamiliar.id == data.get(pid_key),
            PersonaFamiliar.caso_id == caso_id
        ).first()
        if not p:
            raise HTTPException(status_code=400, detail=f"Persona {pid_key} no pertenece al caso")

    relacion = RelacionFamiliar(
        caso_id=caso_id,
        persona_origen_id=data.get("persona_origen_id"),
        persona_destino_id=data.get("persona_destino_id"),
        tipo_relacion=TipoRelacionFamiliar(data.get("tipo_relacion", "biologica")),
        descripcion=data.get("descripcion"),
        bidireccional=data.get("bidireccional", True),
    )
    db.add(relacion)
    db.commit()
    db.refresh(relacion)
    return relacion

def listar_relaciones(db: Session, caso_id: int) -> list[dict]:
    relaciones = db.query(RelacionFamiliar).filter(RelacionFamiliar.caso_id == caso_id).all()
    return [
        {
            "id": r.id,
            "caso_id": r.caso_id,
            "persona_origen_id": r.persona_origen_id,
            "persona_destino_id": r.persona_destino_id,
            "persona_origen_nombre": r.persona_origen.nombre if r.persona_origen else None,
            "persona_destino_nombre": r.persona_destino.nombre if r.persona_destino else None,
            "tipo_relacion": r.tipo_relacion.value,
            "descripcion": r.descripcion,
            "bidireccional": r.bidireccional,
            "fecha_creacion": r.fecha_creacion,
        }
        for r in relaciones
    ]

def actualizar_relacion(db: Session, relacion_id: int, caso_id: int, data: dict) -> RelacionFamiliar:
    relacion = db.query(RelacionFamiliar).filter(
        RelacionFamiliar.id == relacion_id,
        RelacionFamiliar.caso_id == caso_id
    ).first()
    if not relacion:
        raise HTTPException(status_code=404, detail="Relación no encontrada")
    if "tipo_relacion" in data and data["tipo_relacion"]:
        relacion.tipo_relacion = TipoRelacionFamiliar(data["tipo_relacion"])
    if "descripcion" in data:
        relacion.descripcion = data["descripcion"]
    if "bidireccional" in data and data["bidireccional"] is not None:
        relacion.bidireccional = data["bidireccional"]
    db.commit()
    db.refresh(relacion)
    return relacion

def eliminar_relacion(db: Session, relacion_id: int, caso_id: int):
    relacion = db.query(RelacionFamiliar).filter(
        RelacionFamiliar.id == relacion_id,
        RelacionFamiliar.caso_id == caso_id
    ).first()
    if not relacion:
        raise HTTPException(status_code=404, detail="Relación no encontrada")
    db.delete(relacion)
    db.commit()

# ── ObservacionNoVerbal ──────────────────────

def crear_observacion(db: Session, caso_id: int, data: dict, registrada_por_id: int) -> ObservacionNoVerbal:
    obs = ObservacionNoVerbal(
        caso_id=caso_id,
        persona_familiar_id=data.get("persona_familiar_id"),
        postura=data.get("postura"),
        tono_voz=data.get("tono_voz"),
        expresion_emocional=data.get("expresion_emocional", []),
        estado_fisico=data.get("estado_fisico", []),
        nivel_resistencia=data.get("nivel_resistencia"),
        interpretacion_sugerida=data.get("interpretacion_sugerida"),
        registrada_por_id=registrada_por_id
    )
    db.add(obs)
    db.commit()
    db.refresh(obs)
    return obs

def listar_observaciones(db: Session, caso_id: int) -> list[dict]:
    observaciones = (
        db.query(ObservacionNoVerbal)
        .filter(ObservacionNoVerbal.caso_id == caso_id)
        .order_by(ObservacionNoVerbal.fecha_creacion.desc())
        .all()
    )
    return [
        {
            "id": obs.id,
            "caso_id": obs.caso_id,
            "persona_familiar_id": obs.persona_familiar_id,
            "persona_nombre": obs.persona.nombre if obs.persona else "Desconocido",
            "postura": obs.postura,
            "tono_voz": obs.tono_voz,
            "expresion_emocional": obs.expresion_emocional,
            "estado_fisico": obs.estado_fisico,
            "nivel_resistencia": obs.nivel_resistencia,
            "interpretacion_sugerida": obs.interpretacion_sugerida,
            "registrada_por_id": obs.registrada_por_id,
            "fecha_creacion": obs.fecha_creacion
        }
        for obs in observaciones
    ]

# ── Plan de Acción ───────────────────────────

def generar_plan_accion(db: Session, caso_id: int, creador_id: int) -> dict:
    entrevista = db.query(EntrevistaFamilia).filter(EntrevistaFamilia.caso_id == caso_id).first()
    if not entrevista:
        raise HTTPException(status_code=400, detail="No se puede generar plan sin entrevista")

    if entrevista.proceso_id:
        return proceso_service.obtener_proceso(db, entrevista.proceso_id)

    caso = db.query(CasoNNA).filter(CasoNNA.id == caso_id).first()
    nivel = entrevista.grado_negacion or 1
    fecha_str = datetime.now().strftime("%Y-%m-%d")
    titulo = f"Plan de Acción — Caso NNA-{caso_id} — {fecha_str}"

    proceso = proceso_service.crear_proceso(
        db=db, titulo=titulo,
        descripcion=f"Plan de acción generado automáticamente para {caso.nna_nombre} (Nivel de negación {nivel})",
        expediente_id=None, creador_id=creador_id, usuario_ids=[]
    )

    if nivel == 1:
        subtareas = [
            "Elaborar plan de acción colaborativo con la familia",
            "Agendar visita de seguimiento",
            "Identificar redes de apoyo comunitario"
        ]
    elif nivel == 2:
        subtareas = [
            "Documentar negación en expediente",
            "Consultar con equipo multidisciplinario",
            "Definir medidas de seguimiento reforzado",
            "Agendar segunda entrevista"
        ]
    else:
        subtareas = [
            "Escalar a coordinación inmediatamente",
            "Evaluar medidas de protección especial urgentes",
            "Documentar situación de riesgo grave",
            "Iniciar protocolo de separación temporal si aplica"
        ]

    for sub_tit in subtareas:
        proceso_service.agregar_subtarea(db, proceso.id, sub_tit)

    entrevista.proceso_id = proceso.id
    db.commit()
    return proceso_service.obtener_proceso(db, proceso.id)

def obtener_plan_accion(db: Session, caso_id: int) -> dict | None:
    entrevista = db.query(EntrevistaFamilia).filter(EntrevistaFamilia.caso_id == caso_id).first()
    if not entrevista or not entrevista.proceso_id:
        return None
    return proceso_service.obtener_proceso(db, entrevista.proceso_id)
