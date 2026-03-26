from sqlalchemy import Column, Integer, String, Boolean, Text, TIMESTAMP, Date
from sqlalchemy.sql import func
from datetime import date as date_type
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), nullable=False)
    apellido_paterno = Column(String(50), nullable=False)
    apellido_materno = Column(String(50), nullable=False)
    rfc = Column(String(13), nullable=False)
    curp = Column(String(18), nullable=False)
    sexo = Column(String(10), nullable=False)
    fecha_nacimiento = Column(Date, nullable=False)
    edad = Column(Integer, nullable=False)
    estado = Column(String(50), nullable=False)
    municipio = Column(String(100), nullable=False)
    colonia = Column(String(100), nullable=False)
    calle = Column(String(100), nullable=False)
    numero = Column(String(20), nullable=False)
    codigo_postal = Column(String(5), nullable=False)
    calles_aledanas = Column(Text, nullable=True)
    tipo_personal = Column(String(20), nullable=False)
    rol = Column(String(30), nullable=False)
    correo = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    activo = Column(Boolean, default=True)
    verificado = Column(Boolean, default=False)
    foto_perfil = Column(String(500), nullable=True, default=None)
    fecha_creacion = Column(TIMESTAMP, server_default=func.now())

    @property
    def edad_actual(self) -> int:
        """Calcula la edad dinámicamente desde fecha_nacimiento."""
        today = date_type.today()
        return today.year - self.fecha_nacimiento.year - (
            (today.month, today.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day)
        )

