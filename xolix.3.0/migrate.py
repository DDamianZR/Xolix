"""Migración: agregar columna foto_perfil a users."""
import psycopg2

conn = psycopg2.connect(
    dbname="proyecto_escom",
    user="postgres",
    password="12345",
    host="localhost",
)
cur = conn.cursor()
cur.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS foto_perfil VARCHAR(500) DEFAULT NULL")
conn.commit()
print("✅ Migración aplicada: columna foto_perfil agregada")
conn.close()
