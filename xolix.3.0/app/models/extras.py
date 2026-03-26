from sqlalchemy import Column, Integer, String, Text, Boolean, TIMESTAMP, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    accion = Column(String(100), nullable=False) # e.g., "DELETE_USER", "UPLOAD_FILE"
    entidad = Column(String(50), nullable=False) # e.g., "user", "expediente", "proceso"
    entidad_id = Column(Integer, nullable=True)
    detalles = Column(JSON, nullable=True)
    fecha = Column(TIMESTAMP, server_default=func.now())

    # Relationship
    usuario = relationship("User")

class Comentario(Base):
    __tablename__ = "comentarios"

    id = Column(Integer, primary_key=True, index=True)
    proceso_id = Column(Integer, ForeignKey("procesos.id", ondelete="CASCADE"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    texto = Column(Text, nullable=False)
    fecha = Column(TIMESTAMP, server_default=func.now())

    # Relationships
    proceso = relationship("Proceso", backref="comentarios_list")
    usuario = relationship("User")

class Notificacion(Base):
    __tablename__ = "notificaciones"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    mensaje = Column(String(500), nullable=False)
    tipo = Column(String(50), nullable=False, default="info") # info, success, warning, error
    leida = Column(Boolean, default=False)
    fecha = Column(TIMESTAMP, server_default=func.now())

    # Relationship
    usuario = relationship("User", backref="notificaciones")
