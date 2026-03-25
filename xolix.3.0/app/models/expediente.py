from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ForeignKey, Enum as SAEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class PermisoExpediente(str, enum.Enum):
    lectura = "lectura"
    edicion = "edicion"


class Expediente(Base):
    __tablename__ = "expedientes"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(200), nullable=False)
    descripcion = Column(Text, nullable=True)
    archivo_path = Column(String(500), nullable=False)
    tipo_archivo = Column(String(50), nullable=False, default="pdf")
    propietario_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    fecha_creacion = Column(TIMESTAMP, server_default=func.now())
    fecha_actualizacion = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationships
    propietario = relationship("User", backref="expedientes")
    compartidos = relationship("ExpedienteCompartido", back_populates="expediente", cascade="all, delete-orphan")


class ExpedienteCompartido(Base):
    __tablename__ = "expedientes_compartidos"

    id = Column(Integer, primary_key=True, index=True)
    expediente_id = Column(Integer, ForeignKey("expedientes.id", ondelete="CASCADE"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    permiso = Column(SAEnum(PermisoExpediente), default=PermisoExpediente.lectura, nullable=False)
    fecha_compartido = Column(TIMESTAMP, server_default=func.now())

    # Relationships
    expediente = relationship("Expediente", back_populates="compartidos")
    usuario = relationship("User")
