from sqlalchemy import Column, Integer, String, Text, Boolean, TIMESTAMP, ForeignKey, Enum as SAEnum, JSON
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

class CasoNNA(Base):
    __tablename__ = "nna_casos"

    id = Column(Integer, primary_key=True, index=True)
    nna_nombre = Column(String(200), nullable=False)
    nna_edad = Column(Integer, nullable=True)
    nna_genero = Column(SAEnum(GeneroNNA), nullable=True)
    estado = Column(SAEnum(EstadoCasoNNA), default=EstadoCasoNNA.activo, nullable=False)
    creador_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    fecha_creacion = Column(TIMESTAMP, server_default=func.now())
    fecha_actualizacion = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    creador = relationship("User", foreign_keys=[creador_id])
    entrevista = relationship("EntrevistaFamilia", back_populates="caso", uselist=False, cascade="all, delete-orphan")
    personas = relationship("PersonaFamiliar", back_populates="caso", cascade="all, delete-orphan")
    familiograma = relationship("Familiograma", back_populates="caso", uselist=False, cascade="all, delete-orphan")
    observaciones = relationship("ObservacionNoVerbal", back_populates="caso", cascade="all, delete-orphan")


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
    fecha_creacion = Column(TIMESTAMP, server_default=func.now())

    caso = relationship("CasoNNA", back_populates="personas")
    observaciones_no_verbales = relationship("ObservacionNoVerbal", back_populates="persona", cascade="all, delete-orphan")


class Familiograma(Base):
    __tablename__ = "nna_familiogramas"

    id = Column(Integer, primary_key=True, index=True)
    caso_id = Column(Integer, ForeignKey("nna_casos.id", ondelete="CASCADE"), unique=True, nullable=False)
    grafo_json = Column(JSON, nullable=True) # {nodes: [], edges: []}
    imagen_url = Column(Text, nullable=True)
    fecha_actualizacion = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    caso = relationship("CasoNNA", back_populates="familiograma")


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
