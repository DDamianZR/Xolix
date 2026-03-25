from sqlalchemy import Column, Integer, String, Text, Boolean, TIMESTAMP, ForeignKey, Enum as SAEnum, Table
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class EstadoProceso(str, enum.Enum):
    pendiente = "pendiente"
    en_proceso = "en_proceso"
    terminado = "terminado"


# Many-to-many: procesos <-> usuarios
proceso_usuarios = Table(
    "proceso_usuarios",
    Base.metadata,
    Column("proceso_id", Integer, ForeignKey("procesos.id", ondelete="CASCADE"), primary_key=True),
    Column("usuario_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
)


class Proceso(Base):
    __tablename__ = "procesos"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(200), nullable=False)
    descripcion = Column(Text, nullable=True)
    estado = Column(SAEnum(EstadoProceso), default=EstadoProceso.pendiente, nullable=False)
    expediente_id = Column(Integer, ForeignKey("expedientes.id", ondelete="SET NULL"), nullable=True)
    creador_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    fecha_creacion = Column(TIMESTAMP, server_default=func.now())
    fecha_actualizacion = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationships
    subtareas = relationship("Subtarea", back_populates="proceso", cascade="all, delete-orphan")
    usuarios = relationship("User", secondary=proceso_usuarios, backref="procesos")
    expediente = relationship("Expediente")
    creador = relationship("User", foreign_keys=[creador_id])


class Subtarea(Base):
    __tablename__ = "subtareas"

    id = Column(Integer, primary_key=True, index=True)
    proceso_id = Column(Integer, ForeignKey("procesos.id", ondelete="CASCADE"), nullable=False)
    titulo = Column(String(200), nullable=False)
    completada = Column(Boolean, default=False)
    fecha_creacion = Column(TIMESTAMP, server_default=func.now())

    # Relationships
    proceso = relationship("Proceso", back_populates="subtareas")
