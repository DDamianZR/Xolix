from sqlalchemy import Column, Integer, String, Text, Boolean, TIMESTAMP, Date, ForeignKey, Enum as SAEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import enum


# ── Enums ──────────────────────────────────

class EstadoCaso(str, enum.Enum):
    activo = "activo"
    seguimiento = "seguimiento"
    cerrado = "cerrado"
    urgente = "urgente"


class NivelRiesgo(str, enum.Enum):
    bajo = "bajo"
    medio = "medio"
    alto = "alto"
    critico = "critico"


class AreaProfesional(str, enum.Enum):
    psicologia = "psicologia"
    legal = "legal"
    trabajo_social = "trabajo_social"
    medico = "medico"
    analisis = "analisis"
    general = "general"


class TipoViolencia(str, enum.Enum):
    fisica = "fisica"
    psicologica = "psicologica"
    sexual = "sexual"
    abandono = "abandono"
    negligencia = "negligencia"
    otro = "otro"


class PermisoCaso(str, enum.Enum):
    lectura = "lectura"
    escritura = "escritura"
    admin_caso = "admin_caso"


class CategoriaDocumento(str, enum.Enum):
    legal = "legal"
    medico = "medico"
    evidencia = "evidencia"
    psicologico = "psicologico"
    social = "social"
    otro = "otro"


# ── Many-to-many helper ───────────────────

# ── Models ─────────────────────────────────

class Caso(Base):
    __tablename__ = "casos"

    id = Column(Integer, primary_key=True, index=True)
    folio = Column(String(20), unique=True, nullable=False)  # XOL-2026-001
    titulo = Column(String(300), nullable=False)
    descripcion = Column(Text, nullable=True)
    estado = Column(SAEnum(EstadoCaso), default=EstadoCaso.activo, nullable=False)
    nivel_riesgo = Column(SAEnum(NivelRiesgo), default=NivelRiesgo.medio, nullable=False)
    creador_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    fecha_creacion = Column(TIMESTAMP, server_default=func.now())
    fecha_actualizacion = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationships
    creador = relationship("User", foreign_keys=[creador_id])
    hecho_victimal = relationship("HechoVictimal", back_populates="caso", uselist=False, cascade="all, delete-orphan")
    participantes = relationship("CasoParticipante", back_populates="caso", cascade="all, delete-orphan")
    notas = relationship("NotaCaso", back_populates="caso", cascade="all, delete-orphan", order_by="NotaCaso.fecha_creacion.desc()")
    documentos = relationship("DocumentoCaso", back_populates="caso", cascade="all, delete-orphan")


class HechoVictimal(Base):
    __tablename__ = "hechos_victimales"

    id = Column(Integer, primary_key=True, index=True)
    caso_id = Column(Integer, ForeignKey("casos.id", ondelete="CASCADE"), unique=True, nullable=False)

    # Víctima (madre/tutor)
    victima_nombres = Column(String(100), nullable=True)
    victima_apellido_paterno = Column(String(100), nullable=True)
    victima_apellido_materno = Column(String(100), nullable=True)
    victima_curp = Column(String(18), nullable=True)

    # Menor
    menor_nombres = Column(String(100), nullable=True)
    menor_apellido_paterno = Column(String(100), nullable=True)
    menor_apellido_materno = Column(String(100), nullable=True)
    menor_curp = Column(String(18), nullable=True)
    edad_menor = Column(Integer, nullable=True)

    # Hecho
    fecha_incidente = Column(Date, nullable=True)
    ubicacion = Column(String(300), nullable=True)
    descripcion_delito = Column(Text, nullable=True)
    tipo_violencia = Column(SAEnum(TipoViolencia), nullable=True)
    referencia_juridica = Column(String(200), nullable=True)
    referencia_fud = Column(String(200), nullable=True)

    # Metadata
    fecha_creacion_expediente = Column(TIMESTAMP, server_default=func.now())
    consideraciones = Column(Text, nullable=True)

    # Relationships
    caso = relationship("Caso", back_populates="hecho_victimal")


class CasoParticipante(Base):
    __tablename__ = "caso_participantes"

    id = Column(Integer, primary_key=True, index=True)
    caso_id = Column(Integer, ForeignKey("casos.id", ondelete="CASCADE"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    area = Column(SAEnum(AreaProfesional), nullable=False)
    permiso = Column(SAEnum(PermisoCaso), default=PermisoCaso.escritura, nullable=False)
    fecha_asignacion = Column(TIMESTAMP, server_default=func.now())

    # Relationships
    caso = relationship("Caso", back_populates="participantes")
    usuario = relationship("User")


class NotaCaso(Base):
    __tablename__ = "notas_caso"

    id = Column(Integer, primary_key=True, index=True)
    caso_id = Column(Integer, ForeignKey("casos.id", ondelete="CASCADE"), nullable=False)
    autor_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    area = Column(SAEnum(AreaProfesional), default=AreaProfesional.general, nullable=False)
    contenido = Column(Text, nullable=False)
    privada = Column(Boolean, default=False)
    etiquetas = Column(Text, nullable=True)  # JSON string: ["urgente", "seguimiento"]
    fecha_creacion = Column(TIMESTAMP, server_default=func.now())
    fecha_actualizacion = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationships
    caso = relationship("Caso", back_populates="notas")
    autor = relationship("User")


class DocumentoCaso(Base):
    __tablename__ = "documentos_caso"

    id = Column(Integer, primary_key=True, index=True)
    caso_id = Column(Integer, ForeignKey("casos.id", ondelete="CASCADE"), nullable=False)
    subido_por_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    nombre = Column(String(300), nullable=False)
    archivo_path = Column(String(500), nullable=False)
    tipo_archivo = Column(String(50), nullable=False, default="pdf")
    categoria = Column(SAEnum(CategoriaDocumento), default=CategoriaDocumento.otro, nullable=False)
    version = Column(Integer, default=1)
    fecha_subida = Column(TIMESTAMP, server_default=func.now())

    # Relationships
    caso = relationship("Caso", back_populates="documentos")
    subido_por = relationship("User")
