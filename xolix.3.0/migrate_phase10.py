"""Script para recrear la base de datos con el nuevo esquema de la Fase 10."""
from app.database import engine, Base
from app.models import user, expediente, proceso

def migrate():
    print("Eliminando tablas existentes...")
    Base.metadata.drop_all(bind=engine)
    print("Creando nuevas tablas...")
    Base.metadata.create_all(bind=engine)
    print("¡Base de datos migrada exitosamente (Fase 10)!")

if __name__ == "__main__":
    migrate()
