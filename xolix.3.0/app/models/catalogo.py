from sqlalchemy import Column, Integer, String, Text, Boolean, TIMESTAMP, ForeignKey, Enum as SAEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class CategoriaDerecho(str, enum.Enum):
    salud = "salud"
    educacion = "educacion"
    identidad = "identidad"
    familia = "familia"
    proteccion = "proteccion"
    participacion = "participacion"
    alimentacion = "alimentacion"
    vivienda = "vivienda"
    otro = "otro"


class Derecho(Base):
    __tablename__ = "derechos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(200), nullable=False)
    descripcion = Column(Text, nullable=True)
    categoria = Column(SAEnum(CategoriaDerecho), nullable=False, default=CategoriaDerecho.proteccion)
    articulo_referencia = Column(String(200), nullable=True)
    activo = Column(Boolean, default=True)
    fecha_creacion = Column(TIMESTAMP, server_default=func.now())

    indicadores = relationship("Indicador", back_populates="derecho", cascade="all, delete-orphan")


class Indicador(Base):
    __tablename__ = "indicadores"

    id = Column(Integer, primary_key=True, index=True)
    derecho_id = Column(Integer, ForeignKey("derechos.id", ondelete="CASCADE"), nullable=False)
    nombre = Column(String(300), nullable=False)
    descripcion = Column(Text, nullable=True)
    tipo_evaluacion = Column(String(50), nullable=True, default="si_no")  # si_no, escala, texto
    activo = Column(Boolean, default=True)
    fecha_creacion = Column(TIMESTAMP, server_default=func.now())

    derecho = relationship("Derecho", back_populates="indicadores")
