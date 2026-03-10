from sqlalchemy import Column, Integer, String, Boolean, Text, TIMESTAMP
from sqlalchemy.sql import func
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    nombre_completo = Column(String(150), nullable=False)
    rfc = Column(String(13), nullable=False)
    curp = Column(String(18), nullable=False)
    sexo = Column(String(10), nullable=False)
    edad = Column(Integer, nullable=False)
    direccion = Column(Text, nullable=False)
    tipo_personal = Column(String(20), nullable=False)
    rol = Column(String(30), nullable=False)
    correo = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    activo = Column(Boolean, default=True)
    fecha_creacion = Column(TIMESTAMP, server_default=func.now())
