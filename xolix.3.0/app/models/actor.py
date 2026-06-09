from sqlalchemy import Column, Integer, String, Text, Boolean, TIMESTAMP, Numeric, ForeignKey, Enum as SAEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class TipoActor(str, enum.Enum):
    gobierno = "gobierno"
    civil = "civil"
    empresa = "empresa"
    persona_fisica = "persona_fisica"


class TipoServicio(str, enum.Enum):
    servicio = "servicio"
    producto = "producto"


class Actor(Base):
    __tablename__ = "actores"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(300), nullable=False)
    tipo = Column(SAEnum(TipoActor), nullable=False)
    descripcion = Column(Text, nullable=True)
    # Contacto
    direccion = Column(String(300), nullable=True)
    municipio = Column(String(100), nullable=True)
    estado = Column(String(100), nullable=True)
    pais = Column(String(100), nullable=True, default="México")
    telefono = Column(String(30), nullable=True)
    correo = Column(String(150), nullable=True)
    sitio_web = Column(String(300), nullable=True)
    redes_sociales = Column(Text, nullable=True)  # JSON string
    activo = Column(Boolean, default=True)
    fecha_creacion = Column(TIMESTAMP, server_default=func.now())
    fecha_actualizacion = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    responsables = relationship("ResponsableActor", back_populates="actor", cascade="all, delete-orphan")
    horarios = relationship("HorarioActor", back_populates="actor", cascade="all, delete-orphan")
    servicios = relationship("ServicioActor", back_populates="actor", cascade="all, delete-orphan")


class ResponsableActor(Base):
    __tablename__ = "actores_responsables"

    id = Column(Integer, primary_key=True, index=True)
    actor_id = Column(Integer, ForeignKey("actores.id", ondelete="CASCADE"), nullable=False)
    nombre = Column(String(200), nullable=False)
    cargo = Column(String(150), nullable=True)
    telefono = Column(String(30), nullable=True)
    correo = Column(String(150), nullable=True)
    es_principal = Column(Boolean, default=False)
    fecha_creacion = Column(TIMESTAMP, server_default=func.now())

    actor = relationship("Actor", back_populates="responsables")


class HorarioActor(Base):
    __tablename__ = "actores_horarios"

    id = Column(Integer, primary_key=True, index=True)
    actor_id = Column(Integer, ForeignKey("actores.id", ondelete="CASCADE"), nullable=False)
    dia_semana = Column(String(20), nullable=False)  # lunes, martes...
    hora_inicio = Column(String(10), nullable=True)
    hora_fin = Column(String(10), nullable=True)
    activo = Column(Boolean, default=True)

    actor = relationship("Actor", back_populates="horarios")


class ServicioActor(Base):
    __tablename__ = "actores_servicios"

    id = Column(Integer, primary_key=True, index=True)
    actor_id = Column(Integer, ForeignKey("actores.id", ondelete="CASCADE"), nullable=False)
    derecho_id = Column(Integer, ForeignKey("derechos.id", ondelete="SET NULL"), nullable=True)
    nombre = Column(String(300), nullable=False)
    descripcion = Column(Text, nullable=True)
    tipo = Column(SAEnum(TipoServicio), default=TipoServicio.servicio, nullable=False)
    es_gratuito = Column(Boolean, default=True)
    costo = Column(Numeric(10, 2), nullable=True)
    disponibilidad = Column(String(100), nullable=True)
    duracion_estimada = Column(String(100), nullable=True)
    activo = Column(Boolean, default=True)
    fecha_creacion = Column(TIMESTAMP, server_default=func.now())

    actor = relationship("Actor", back_populates="servicios")
    derecho = relationship("Derecho")
    requisitos = relationship("RequisitoServicio", back_populates="servicio", cascade="all, delete-orphan")


class RequisitoServicio(Base):
    __tablename__ = "servicios_requisitos"

    id = Column(Integer, primary_key=True, index=True)
    servicio_id = Column(Integer, ForeignKey("actores_servicios.id", ondelete="CASCADE"), nullable=False)
    descripcion = Column(String(500), nullable=False)
    procedimiento_acceso = Column(Text, nullable=True)
    documentacion_requerida = Column(Text, nullable=True)
    fecha_creacion = Column(TIMESTAMP, server_default=func.now())

    servicio = relationship("ServicioActor", back_populates="requisitos")
