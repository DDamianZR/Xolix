from sqlalchemy import Column, Integer, String, Text, Boolean, TIMESTAMP, Date, ForeignKey, Enum as SAEnum, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import enum

class GeneroNNA(str, enum.Enum):
    masculino = "masculino"
    femenino = "femenino"
    no_binario = "no_binario"
    otro = "otro"

class EstadoCasoNNA(str, enum.Enum):
    activo = "activo"
    cerrado = "cerrado"

class TipoSimboloFamiliar(str, enum.Enum):
    normal = "normal"
    clave = "clave"
    fallecido = "fallecido"
    cuidador = "cuidador"
    agresor = "agresor"

class TipoRelacionFamiliar(str, enum.Enum):
    biologica = "biologica"
    legal = "legal"
    emocional_positiva = "emocional_positiva"
    conflictiva = "conflictiva"
    protectora = "protectora"
    dependencia = "dependencia"
    separacion = "separacion"
    desconocida = "desconocida"

class CasoNNA(Base):
    __tablename__ = "nna_casos"

    id = Column(Integer, primary_key=True, index=True)
    nna_nombre = Column(String(200), nullable=False)
    nna_curp = Column(String(18), nullable=True)
    nna_fecha_nacimiento = Column(Date, nullable=True)
    nna_edad = Column(Integer, nullable=True)
    nna_genero = Column(SAEnum(GeneroNNA), nullable=True)
    nna_nacionalidad = Column(String(100), nullable=True, default="Mexicana")
    nna_estado_civil = Column(String(50), nullable=True)
    estado = Column(SAEnum(EstadoCasoNNA), default=EstadoCasoNNA.activo, nullable=False)
    creador_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    responsable_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    fecha_creacion = Column(TIMESTAMP, server_default=func.now())
    fecha_actualizacion = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    creador      = relationship("User", foreign_keys=[creador_id])
    responsable  = relationship("User", foreign_keys=[responsable_id])
    equipo       = relationship("EquipoCaso", back_populates="caso", cascade="all, delete-orphan")
    entrevista = relationship("EntrevistaFamilia", back_populates="caso", uselist=False, cascade="all, delete-orphan")
    personas = relationship("PersonaFamiliar", back_populates="caso", cascade="all, delete-orphan")
    familiograma = relationship("Familiograma", back_populates="caso", uselist=False, cascade="all, delete-orphan")
    observaciones = relationship("ObservacionNoVerbal", back_populates="caso", cascade="all, delete-orphan")
    relaciones = relationship("RelacionFamiliar", back_populates="caso", cascade="all, delete-orphan")
    tutor = relationship("TutorNNA", back_populates="caso", uselist=False, cascade="all, delete-orphan")
    datos_medicos = relationship("DatosMedicosNNA", back_populates="caso", uselist=False, cascade="all, delete-orphan")


class EntrevistaFamilia(Base):
    __tablename__ = "nna_entrevistas"

    id = Column(Integer, primary_key=True, index=True)
    caso_id = Column(Integer, ForeignKey("nna_casos.id", ondelete="CASCADE"), unique=True, nullable=False)
    fecha = Column(TIMESTAMP, server_default=func.now())
    frases_comunicadas = Column(JSON, nullable=True) # [{id, texto, comunicada, notas}]
    dia_comun = Column(JSON, nullable=True) # {quien_despierta, rutina_matutina...}
    grado_negacion = Column(Integer, default=1) # 1, 2, 3
    observaciones_negacion = Column(Text, nullable=True)
    completada = Column(Boolean, default=False)
    proceso_id = Column(Integer, ForeignKey("procesos.id", ondelete="SET NULL"), nullable=True)

    caso = relationship("CasoNNA", back_populates="entrevista")


class PersonaFamiliar(Base):
    __tablename__ = "nna_personas"

    id = Column(Integer, primary_key=True, index=True)
    caso_id = Column(Integer, ForeignKey("nna_casos.id", ondelete="CASCADE"), nullable=False)
    nombre = Column(String(200), nullable=False)
    edad = Column(Integer, nullable=True)
    genero = Column(SAEnum(GeneroNNA), nullable=True)
    rol_en_familia = Column(String(100), nullable=True)
    tipo_simbolo = Column(SAEnum(TipoSimboloFamiliar), default=TipoSimboloFamiliar.normal)
    observaciones = Column(Text, nullable=True)
    # Campos extendidos (iteración 2)
    telefono = Column(String(20), nullable=True)
    direccion = Column(String(300), nullable=True)
    ocupacion = Column(String(150), nullable=True)
    escolaridad = Column(String(100), nullable=True)
    estado_salud = Column(String(200), nullable=True)
    vive_con_nna = Column(Boolean, default=False)
    es_responsable_legal = Column(Boolean, default=False)
    fecha_creacion = Column(TIMESTAMP, server_default=func.now())

    caso = relationship("CasoNNA", back_populates="personas")
    observaciones_no_verbales = relationship("ObservacionNoVerbal", back_populates="persona", cascade="all, delete-orphan")
    relaciones_origen = relationship(
        "RelacionFamiliar", foreign_keys="RelacionFamiliar.persona_origen_id",
        back_populates="persona_origen", cascade="all, delete-orphan"
    )
    relaciones_destino = relationship(
        "RelacionFamiliar", foreign_keys="RelacionFamiliar.persona_destino_id",
        back_populates="persona_destino", cascade="all, delete-orphan"
    )


class Familiograma(Base):
    __tablename__ = "nna_familiogramas"

    id = Column(Integer, primary_key=True, index=True)
    caso_id = Column(Integer, ForeignKey("nna_casos.id", ondelete="CASCADE"), unique=True, nullable=False)
    grafo_json = Column(JSON, nullable=True) # {nodes: [], edges: []}
    imagen_url = Column(Text, nullable=True)
    fecha_actualizacion = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    caso = relationship("CasoNNA", back_populates="familiograma")
    historial = relationship(
        "HistorialFamiliograma", back_populates="familiograma",
        cascade="all, delete-orphan", order_by="HistorialFamiliograma.fecha.desc()"
    )


class HistorialFamiliograma(Base):
    """Versión guardada del familiograma — se genera automáticamente en cada save."""
    __tablename__ = "nna_historial_familiograma"

    id = Column(Integer, primary_key=True, index=True)
    familiograma_id = Column(Integer, ForeignKey("nna_familiogramas.id", ondelete="CASCADE"), nullable=False)
    caso_id = Column(Integer, ForeignKey("nna_casos.id", ondelete="CASCADE"), nullable=False)
    version = Column(Integer, nullable=False, default=1)
    grafo_json = Column(JSON, nullable=True)
    modificado_por_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    notas_version = Column(String(500), nullable=True)
    fecha = Column(TIMESTAMP, server_default=func.now())

    familiograma = relationship("Familiograma", back_populates="historial")
    modificado_por = relationship("User")


class RelacionFamiliar(Base):
    """Arista tipificada entre dos PersonaFamiliar en el familiograma."""
    __tablename__ = "nna_relaciones_familiares"

    id = Column(Integer, primary_key=True, index=True)
    caso_id = Column(Integer, ForeignKey("nna_casos.id", ondelete="CASCADE"), nullable=False)
    persona_origen_id = Column(Integer, ForeignKey("nna_personas.id", ondelete="CASCADE"), nullable=False)
    persona_destino_id = Column(Integer, ForeignKey("nna_personas.id", ondelete="CASCADE"), nullable=False)
    tipo_relacion = Column(SAEnum(TipoRelacionFamiliar), default=TipoRelacionFamiliar.biologica, nullable=False)
    descripcion = Column(Text, nullable=True)
    bidireccional = Column(Boolean, default=True)
    fecha_creacion = Column(TIMESTAMP, server_default=func.now())

    caso = relationship("CasoNNA", back_populates="relaciones")
    persona_origen = relationship("PersonaFamiliar", foreign_keys=[persona_origen_id], back_populates="relaciones_origen")
    persona_destino = relationship("PersonaFamiliar", foreign_keys=[persona_destino_id], back_populates="relaciones_destino")


class ObservacionNoVerbal(Base):
    __tablename__ = "nna_observaciones"

    id = Column(Integer, primary_key=True, index=True)
    caso_id = Column(Integer, ForeignKey("nna_casos.id", ondelete="CASCADE"), nullable=False)
    persona_familiar_id = Column(Integer, ForeignKey("nna_personas.id", ondelete="CASCADE"), nullable=False)
    postura = Column(String(200), nullable=True)
    tono_voz = Column(String(100), nullable=True)
    expresion_emocional = Column(JSON, nullable=True) # list of strings
    estado_fisico = Column(JSON, nullable=True) # list of strings
    nivel_resistencia = Column(String(100), nullable=True)
    interpretacion_sugerida = Column(Text, nullable=True)
    registrada_por_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    fecha_creacion = Column(TIMESTAMP, server_default=func.now())

    caso = relationship("CasoNNA", back_populates="observaciones")
    persona = relationship("PersonaFamiliar", back_populates="observaciones_no_verbales")
    registrada_por = relationship("User")


class TutorNNA(Base):
    __tablename__ = "nna_tutores"

    id = Column(Integer, primary_key=True, index=True)
    caso_id = Column(Integer, ForeignKey("nna_casos.id", ondelete="CASCADE"), unique=True, nullable=False)
    nombre = Column(String(200), nullable=False)
    apellido_paterno = Column(String(100), nullable=True)
    apellido_materno = Column(String(100), nullable=True)
    curp = Column(String(18), nullable=True)
    rfc = Column(String(13), nullable=True)
    parentesco = Column(String(100), nullable=True)
    telefono = Column(String(20), nullable=True)
    correo = Column(String(100), nullable=True)
    direccion = Column(String(300), nullable=True)
    ocupacion = Column(String(150), nullable=True)
    documento_identificacion = Column(String(200), nullable=True)
    numero_documento = Column(String(100), nullable=True)
    fecha_creacion = Column(TIMESTAMP, server_default=func.now())
    fecha_actualizacion = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    caso = relationship("CasoNNA", back_populates="tutor")


class DatosMedicosNNA(Base):
    __tablename__ = "nna_datos_medicos"

    id = Column(Integer, primary_key=True, index=True)
    caso_id = Column(Integer, ForeignKey("nna_casos.id", ondelete="CASCADE"), unique=True, nullable=False)
    historial_medico = Column(Text, nullable=True)
    alergias = Column(Text, nullable=True)
    discapacidades = Column(Text, nullable=True)
    cartilla_vacunacion = Column(JSON, nullable=True)  # [{vacuna, fecha, dosis}]
    tipo_sangre = Column(String(10), nullable=True)
    medico_responsable = Column(String(200), nullable=True)
    institucion_medica = Column(String(200), nullable=True)
    fecha_ultimo_chequeo = Column(Date, nullable=True)
    fecha_creacion = Column(TIMESTAMP, server_default=func.now())
    fecha_actualizacion = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    caso = relationship("CasoNNA", back_populates="datos_medicos")
