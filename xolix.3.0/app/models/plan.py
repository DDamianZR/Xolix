from sqlalchemy import Column, Integer, String, Text, Boolean, TIMESTAMP, Date, Numeric, ForeignKey, Enum as SAEnum, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class EstadoPlan(str, enum.Enum):
    borrador = "borrador"
    activo = "activo"
    pausado = "pausado"
    completado = "completado"
    cancelado = "cancelado"


class EstadoMedida(str, enum.Enum):
    pendiente = "pendiente"
    en_proceso = "en_proceso"
    completada = "completada"
    cancelada = "cancelada"


class TipoMedida(str, enum.Enum):
    psicologica = "psicologica"
    legal = "legal"
    medica = "medica"
    educativa = "educativa"
    social = "social"
    economica = "economica"
    otra = "otra"


class PlanRestitucion(Base):
    __tablename__ = "planes_restitucion"

    id = Column(Integer, primary_key=True, index=True)
    caso_nna_id = Column(Integer, ForeignKey("nna_casos.id", ondelete="CASCADE"), nullable=False)
    objetivo = Column(Text, nullable=False)
    derechos_afectados = Column(JSON, nullable=True)  # [derecho_id, ...]
    responsable_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    fecha_inicio = Column(Date, nullable=True)
    fecha_termino = Column(Date, nullable=True)
    estado = Column(SAEnum(EstadoPlan), default=EstadoPlan.borrador, nullable=False)
    observaciones = Column(Text, nullable=True)
    fecha_creacion = Column(TIMESTAMP, server_default=func.now())
    fecha_actualizacion = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    caso_nna = relationship("CasoNNA")
    responsable = relationship("User")
    medidas = relationship("MedidaRestitucion", back_populates="plan", cascade="all, delete-orphan")


class MedidaRestitucion(Base):
    __tablename__ = "medidas_restitucion"

    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey("planes_restitucion.id", ondelete="CASCADE"), nullable=False)
    tipo = Column(SAEnum(TipoMedida), nullable=False, default=TipoMedida.otra)
    descripcion = Column(Text, nullable=False)
    responsable_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    actor_id = Column(Integer, ForeignKey("actores.id", ondelete="SET NULL"), nullable=True)
    recursos_requeridos = Column(Text, nullable=True)
    estado = Column(SAEnum(EstadoMedida), default=EstadoMedida.pendiente, nullable=False)
    porcentaje_avance = Column(Integer, default=0)
    fecha_inicio = Column(Date, nullable=True)
    fecha_limite = Column(Date, nullable=True)
    fecha_creacion = Column(TIMESTAMP, server_default=func.now())
    fecha_actualizacion = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    plan = relationship("PlanRestitucion", back_populates="medidas")
    responsable = relationship("User")
    actor = relationship("Actor")
    seguimientos = relationship("SeguimientoMedida", back_populates="medida", cascade="all, delete-orphan")


class SeguimientoMedida(Base):
    __tablename__ = "seguimientos_medida"

    id = Column(Integer, primary_key=True, index=True)
    medida_id = Column(Integer, ForeignKey("medidas_restitucion.id", ondelete="CASCADE"), nullable=False)
    registrado_por_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    fecha_seguimiento = Column(Date, nullable=False)
    descripcion_avance = Column(Text, nullable=False)
    porcentaje_cumplimiento = Column(Integer, default=0)
    observaciones = Column(Text, nullable=True)
    evidencias = Column(JSON, nullable=True)  # [{nombre, archivo_path}]
    fecha_creacion = Column(TIMESTAMP, server_default=func.now())

    medida = relationship("MedidaRestitucion", back_populates="seguimientos")
    registrado_por = relationship("User")
