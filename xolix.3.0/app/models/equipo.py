from sqlalchemy import Column, Integer, String, Boolean, Text, TIMESTAMP, ForeignKey, CheckConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class EquipoCaso(Base):
    __tablename__ = "nna_equipo_caso"

    id               = Column(Integer, primary_key=True, index=True)
    caso_id          = Column(Integer, ForeignKey("nna_casos.id", ondelete="CASCADE"), nullable=False)
    usuario_id       = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    rol_en_equipo    = Column(String(50), nullable=False)
    asignado_por_id  = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    fecha_asignacion = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    activo           = Column(Boolean, default=True, nullable=False)
    observaciones    = Column(Text, nullable=True)

    caso          = relationship("CasoNNA", back_populates="equipo")
    usuario       = relationship("User", foreign_keys=[usuario_id])
    asignado_por  = relationship("User", foreign_keys=[asignado_por_id])


class EvaluacionConfianza(Base):
    __tablename__ = "evaluaciones_confianza"

    id             = Column(Integer, primary_key=True, index=True)
    usuario_id     = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    evaluador_id   = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    nivel_anterior = Column(Integer, nullable=False)
    nivel_nuevo    = Column(Integer, nullable=False)
    justificacion  = Column(Text, nullable=False)
    fecha          = Column(TIMESTAMP, server_default=func.now(), nullable=False)

    usuario   = relationship("User", foreign_keys=[usuario_id])
    evaluador = relationship("User", foreign_keys=[evaluador_id])
