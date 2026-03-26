"""Crear usuario director para testing."""
import psycopg2
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
password_hash = pwd_context.hash("1234")

conn = psycopg2.connect(
    dbname="proyecto_escom",
    user="postgres",
    password="12345",
    host="localhost",
)
cur = conn.cursor()

cur.execute("""
    INSERT INTO users (
        nombre, apellido_paterno, apellido_materno, rfc, curp, sexo, fecha_nacimiento,
        edad, estado, municipio, colonia, calle, numero, codigo_postal, calles_aledanas,
        tipo_personal, rol, correo, password, activo, verificado
    ) VALUES (
        'Jennifer', 'Director', 'Prueba',
        'JENX900101AAA',
        'JENX900101MDFRRL09',
        'F', '1990-01-01',
        36, 
        'Ciudad de México', 'Gustavo A. Madero', 'Residencial la Escalera', 'Av. Juan de Dios Bátiz', 'S/N', '07320', 'Casi esquina con Miguel Bernard',
        'empleado', 'director',
        'jennifer@xolix.com',
        %s,
        true,
        true
    )
    ON CONFLICT (correo) DO UPDATE SET password = %s, rol = 'director', activo = true, verificado = true
""", (password_hash, password_hash))

conn.commit()
print("✅ Usuario creado:")
print("   Correo:     jennifer@xolix.com")
print("   Contraseña: 1234")
print("   Rol:        director")
conn.close()
