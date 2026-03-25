"""
Tests para la API de Xolix.
Ejecutar con: python -m pytest tests/ -v
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base
from app.dependencies import get_db
from app.security import hash_password

# ── Test DB (SQLite en memoria) ──────────────────
TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_db():
    """Create tables before each test, drop after."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def admin_token(client):
    """Create an admin user and return a valid token."""
    # Insert admin directly into DB
    db = TestingSessionLocal()
    from app.models.user import User
    from datetime import date
    admin = User(
        nombre="Admin",
        apellido_paterno="Test",
        apellido_materno="Usuario",
        rfc="ADMI850101AAA",
        curp="ADMI850101HDFRRL09",
        sexo="M",
        fecha_nacimiento=date(1985, 1, 1),
        edad=41,
        estado="CDMX",
        municipio="GAM",
        colonia="Aragón",
        calle="Avenida",
        numero="123",
        codigo_postal="07000",
        calles_aledanas=None,
        tipo_personal="empleado",
        rol="director",
        correo="admin@test.com",
        password=hash_password("admin123"),
        activo=True,
    )
    db.add(admin)
    db.commit()
    db.close()

    # Login
    res = client.post("/api/auth/login", json={
        "correo": "admin@test.com",
        "password": "admin123"
    })
    assert res.status_code == 200
    return res.json()["access_token"]


# ═══════════════════════════════════════════════
# AUTH TESTS
# ═══════════════════════════════════════════════

class TestAuth:
    def test_login_success(self, client, admin_token):
        """Admin token fixture already tests successful login."""
        assert admin_token is not None

    def test_login_wrong_password(self, client, admin_token):
        res = client.post("/api/auth/login", json={
            "correo": "admin@test.com",
            "password": "wrong"
        })
        assert res.status_code == 401

    def test_login_nonexistent_user(self, client):
        res = client.post("/api/auth/login", json={
            "correo": "nobody@test.com",
            "password": "password"
        })
        assert res.status_code == 401

    def test_protected_route_no_token(self, client):
        res = client.get("/api/usuarios/")
        assert res.status_code == 401


# ═══════════════════════════════════════════════
# USER CRUD TESTS
# ═══════════════════════════════════════════════

class TestUsers:
    def test_list_users(self, client, admin_token):
        res = client.get("/api/usuarios/", headers={
            "Authorization": f"Bearer {admin_token}"
        })
        assert res.status_code == 200
        assert isinstance(res.json(), list)

    def test_create_user(self, client, admin_token):
        res = client.post("/api/usuarios/", json={
            "nombre": "Juan",
            "apellido_paterno": "Pérez",
            "apellido_materno": "López",
            "rfc": "PEJU900115ABC",
            "curp": "PEJU900115HDFRRL09",
            "sexo": "M",
            "fecha_nacimiento": "1990-01-15",
            "estado": "CDMX",
            "municipio": "GAM",
            "colonia": "Aragón",
            "calle": "Avenida",
            "numero": "123",
            "codigo_postal": "07000",
            "tipo_personal": "empleado",
            "rol": "analista",
            "correo": "juan@test.com",
            "password": "password123"
        }, headers={"Authorization": f"Bearer {admin_token}"})
        assert res.status_code == 200
        assert "id" in res.json()

    def test_create_user_underage(self, client, admin_token):
        res = client.post("/api/usuarios/", json={
            "nombre": "Menor",
            "apellido_paterno": "Test",
            "apellido_materno": "López",
            "rfc": "METE150101AAA",
            "curp": "METE150101HDFRRL09",
            "sexo": "M",
            "fecha_nacimiento": "2015-01-01",
            "estado": "CDMX",
            "municipio": "GAM",
            "colonia": "Aragón",
            "calle": "Avenida",
            "numero": "123",
            "codigo_postal": "07000",
            "tipo_personal": "empleado",
            "rol": "analista",
            "correo": "menor@test.com",
            "password": "password123"
        }, headers={"Authorization": f"Bearer {admin_token}"})
        assert res.status_code == 400
        assert "mayor de 18" in res.json()["detail"]

    def test_get_user_by_id(self, client, admin_token):
        # First create a user
        create_res = client.post("/api/usuarios/", json={
            "nombre": "Test",
            "apellido_paterno": "User",
            "apellido_materno": "Demo",
            "rfc": "TEST900101AAA",
            "curp": "TEST900101HDFRRL09",
            "sexo": "M",
            "fecha_nacimiento": "1990-01-01",
            "estado": "CDMX",
            "municipio": "GAM",
            "colonia": "Aragón",
            "calle": "Avenida",
            "numero": "123",
            "codigo_postal": "07000",
            "tipo_personal": "empleado",
            "rol": "analista",
            "correo": "testuser@test.com",
            "password": "password123"
        }, headers={"Authorization": f"Bearer {admin_token}"})
        user_id = create_res.json()["id"]

        # Get the user
        res = client.get(f"/api/usuarios/{user_id}", headers={
            "Authorization": f"Bearer {admin_token}"
        })
        assert res.status_code == 200
        assert res.json()["correo"] == "testuser@test.com"

    def test_update_user(self, client, admin_token):
        # Create user
        create_res = client.post("/api/usuarios/", json={
            "nombre": "Original",
            "apellido_paterno": "Name",
            "apellido_materno": "Demo",
            "rfc": "ORIG900101AAA",
            "curp": "ORIG900101HDFRRL09",
            "sexo": "M",
            "fecha_nacimiento": "1990-01-01",
            "estado": "CDMX",
            "municipio": "GAM",
            "colonia": "Aragón",
            "calle": "Avenida",
            "numero": "123",
            "codigo_postal": "07000",
            "tipo_personal": "empleado",
            "rol": "analista",
            "correo": "original@test.com",
            "password": "password123"
        }, headers={"Authorization": f"Bearer {admin_token}"})
        user_id = create_res.json()["id"]

        # Update
        res = client.put(f"/api/usuarios/{user_id}", json={
            "nombre": "Updated",
            "apellido_paterno": "Name"
        }, headers={"Authorization": f"Bearer {admin_token}"})
        assert res.status_code == 200

    def test_delete_user(self, client, admin_token):
        # Create user
        create_res = client.post("/api/usuarios/", json={
            "nombre": "Delete",
            "apellido_paterno": "Me",
            "apellido_materno": "Now",
            "rfc": "DELE900101AAA",
            "curp": "DELE900101HDFRRL09",
            "sexo": "M",
            "fecha_nacimiento": "1990-01-01",
            "estado": "CDMX",
            "municipio": "GAM",
            "colonia": "Aragón",
            "calle": "Avenida",
            "numero": "123",
            "codigo_postal": "07000",
            "tipo_personal": "empleado",
            "rol": "analista",
            "correo": "deleteme@test.com",
            "password": "password123"
        }, headers={"Authorization": f"Bearer {admin_token}"})
        user_id = create_res.json()["id"]

        # Delete
        res = client.delete(f"/api/usuarios/{user_id}", headers={
            "Authorization": f"Bearer {admin_token}"
        })
        assert res.status_code == 200

    def test_user_not_found(self, client, admin_token):
        res = client.get("/api/usuarios/9999", headers={
            "Authorization": f"Bearer {admin_token}"
        })
        assert res.status_code == 404


# ═══════════════════════════════════════════════
# HEALTH CHECK
# ═══════════════════════════════════════════════

class TestHealth:
    def test_health_check(self, client):
        res = client.get("/api/health")
        assert res.status_code == 200
        assert res.json()["status"] == "ok"
