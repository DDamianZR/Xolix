from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime

from app.models.nna import (
    CasoNNA, EntrevistaFamilia, PersonaFamiliar, Familiograma, ObservacionNoVerbal,
    EstadoCasoNNA, GeneroNNA, TipoSimboloFamiliar
)
from app.models.user import User
from app.services import proceso_service

# --- CasoNNA ---
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

# --- EntrevistaFamilia ---
def crear_o_actualizar_entrevista(db: Session, caso_id: int, data: dict) -> EntrevistaFamilia:
    entrevista = db.query(EntrevistaFamilia).filter(EntrevistaFamilia.caso_id == caso_id).first()
    
    # Process Pydantic models to dict if necessary
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

# --- PersonaFamiliar ---
def crear_persona(db: Session, caso_id: int, data: dict) -> PersonaFamiliar:
    persona = PersonaFamiliar(
        caso_id=caso_id,
        nombre=data.get("nombre"),
        edad=data.get("edad"),
        genero=GeneroNNA(data.get("genero")) if data.get("genero") else None,
        rol_en_familia=data.get("rol_en_familia"),
        tipo_simbolo=TipoSimboloFamiliar(data.get("tipo_simbolo", "normal")),
        observaciones=data.get("observaciones")
    )
    db.add(persona)
    db.commit()
    db.refresh(persona)
    return persona

def listar_personas(db: Session, caso_id: int) -> list[PersonaFamiliar]:
    return db.query(PersonaFamiliar).filter(PersonaFamiliar.caso_id == caso_id).all()

def actualizar_persona(db: Session, persona_id: int, data: dict) -> PersonaFamiliar:
    persona = db.query(PersonaFamiliar).filter(PersonaFamiliar.id == persona_id).first()
    if not persona:
        raise HTTPException(status_code=404, detail="Persona no encontrada")
        
    if "nombre" in data and data["nombre"]:
        persona.nombre = data["nombre"]
    if "edad" in data:
        persona.edad = data["edad"]
    if "genero" in data and data["genero"]:
        persona.genero = GeneroNNA(data["genero"])
    if "rol_en_familia" in data:
        persona.rol_en_familia = data["rol_en_familia"]
    if "tipo_simbolo" in data and data["tipo_simbolo"]:
        persona.tipo_simbolo = TipoSimboloFamiliar(data["tipo_simbolo"])
    if "observaciones" in data:
        persona.observaciones = data["observaciones"]
        
    db.commit()
    db.refresh(persona)
    return persona

def eliminar_persona(db: Session, persona_id: int):
    persona = db.query(PersonaFamiliar).filter(PersonaFamiliar.id == persona_id).first()
    if not persona:
        raise HTTPException(status_code=404, detail="Persona no encontrada")
    db.delete(persona)
    db.commit()

# --- Familiograma ---
def upsert_familiograma(db: Session, caso_id: int, grafo_json: dict, imagen_url: str = None) -> Familiograma:
    familiograma = db.query(Familiograma).filter(Familiograma.caso_id == caso_id).first()
    if not familiograma:
        familiograma = Familiograma(caso_id=caso_id, grafo_json=grafo_json, imagen_url=imagen_url)
        db.add(familiograma)
    else:
        if grafo_json is not None:
            familiograma.grafo_json = grafo_json
        if imagen_url is not None:
            familiograma.imagen_url = imagen_url
            
    db.commit()
    db.refresh(familiograma)
    return familiograma

def obtener_familiograma(db: Session, caso_id: int) -> Familiograma:
    return db.query(Familiograma).filter(Familiograma.caso_id == caso_id).first()

# --- ObservacionNoVerbal ---
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
    observaciones = db.query(ObservacionNoVerbal).filter(ObservacionNoVerbal.caso_id == caso_id).order_by(ObservacionNoVerbal.fecha_creacion.desc()).all()
    # Serialize with persona_nombre
    result = []
    for obs in observaciones:
        obs_dict = {
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
        result.append(obs_dict)
    return result

# --- Plan de Acción ---
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
    
    # Create process
    proceso = proceso_service.crear_proceso(
        db=db,
        titulo=titulo,
        descripcion=f"Plan de acción generado automáticamente para {caso.nna_nombre} (Nivel de negación {nivel})",
        expediente_id=None,
        creador_id=creador_id,
        usuario_ids=[] # Creator is auto-added
    )
    
    # Add tasks based on level
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
    else: # nivel == 3
        proceso.prioridad = "alta"
        subtareas = [
            "Escalar a coordinación inmediatamente",
            "Evaluar medidas de protección especial urgentes",
            "Documentar situación de riesgo grave",
            "Iniciar protocolo de separación temporal si aplica"
        ]
        
    for sub_tit in subtareas:
        proceso_service.agregar_subtarea(db, proceso.id, sub_tit)
        
    # Link back
    entrevista.proceso_id = proceso.id
    db.commit()
    
    return proceso_service.obtener_proceso(db, proceso.id)

def obtener_plan_accion(db: Session, caso_id: int) -> dict | None:
    entrevista = db.query(EntrevistaFamilia).filter(EntrevistaFamilia.caso_id == caso_id).first()
    if not entrevista or not entrevista.proceso_id:
        return None
    return proceso_service.obtener_proceso(db, entrevista.proceso_id)
