from sqlalchemy import Column, Integer, String, Text, Boolean, TIMESTAMP, Date, ForeignKey, Enum as SAEnum, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class TipoDiagnostico(str, enum.Enum):
    inicial = "inicial"
    nna = "nna"
    tutor = "tutor"
    entorno = "entorno"


class SeveridadVulneracion(str, enum.Enum):
    leve = "leve"
    moderada = "moderada"
    grave = "grave"
    critica = "critica"


class Diagnostico(Base):
    __tablename__ = "diagnosticos"

    id = Column(Integer, primary_key=True, index=True)
    caso_nna_id = Column(Integer, ForeignKey("nna_casos.id", ondelete="CASCADE"), nullable=False)
    tipo = Column(SAEnum(TipoDiagnostico), nullable=False)
    fecha = Column(Date, nullable=False)
    responsable_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    observaciones = Column(Text, nullable=True)
    completado = Column(Boolean, default=False)
    fecha_creacion = Column(TIMESTAMP, server_default=func.now())
    fecha_actualizacion = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    caso_nna = relationship("CasoNNA")
    responsable = relationship("User")
    evidencias = relationship("EvidenciaDiagnostico", back_populates="diagnostico", cascade="all, delete-orphan")
    indicadores_eval = relationship("IndicadorDiagnostico", back_populates="diagnostico", cascade="all, delete-orphan")
    derechos_vulnerados = relationship("DerechoVulnerado", back_populates="diagnostico", cascade="all, delete-orphan")


class EvidenciaDiagnostico(Base):
    __tablename__ = "diagnosticos_evidencias"

    id = Column(Integer, primary_key=True, index=True)
    diagnostico_id = Column(Integer, ForeignKey("diagnosticos.id", ondelete="CASCADE"), nullable=False)
    nombre = Column(String(300), nullable=False)
    archivo_path = Column(String(500), nullable=True)
    descripcion = Column(Text, nullable=True)
    tipo_archivo = Column(String(50), nullable=True)
    fecha_subida = Column(TIMESTAMP, server_default=func.now())

    diagnostico = relationship("Diagnostico", back_populates="evidencias")


class IndicadorDiagnostico(Base):
    __tablename__ = "diagnosticos_indicadores"

    id = Column(Integer, primary_key=True, index=True)
    diagnostico_id = Column(Integer, ForeignKey("diagnosticos.id", ondelete="CASCADE"), nullable=False)
    indicador_id = Column(Integer, ForeignKey("indicadores.id", ondelete="CASCADE"), nullable=False)
    valor = Column(String(100), nullable=True)   # "si", "no", "1-5", texto libre
    observacion = Column(Text, nullable=True)
    vulnerado = Column(Boolean, default=False)
    fecha_creacion = Column(TIMESTAMP, server_default=func.now())

    diagnostico = relationship("Diagnostico", back_populates="indicadores_eval")
    indicador = relationship("Indicador")


class DerechoVulnerado(Base):
    __tablename__ = "diagnosticos_derechos_vulnerados"

    id = Column(Integer, primary_key=True, index=True)
    diagnostico_id = Column(Integer, ForeignKey("diagnosticos.id", ondelete="CASCADE"), nullable=False)
    derecho_id = Column(Integer, ForeignKey("derechos.id", ondelete="CASCADE"), nullable=False)
    severidad = Column(SAEnum(SeveridadVulneracion), default=SeveridadVulneracion.moderada, nullable=False)
    recomendacion = Column(Text, nullable=True)
    generado_automaticamente = Column(Boolean, default=False)
    fecha_creacion = Column(TIMESTAMP, server_default=func.now())

    diagnostico = relationship("Diagnostico", back_populates="derechos_vulnerados")
    derecho = relationship("Derecho")
