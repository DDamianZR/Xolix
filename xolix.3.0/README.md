# 🟣 XOLIX — Sistema de Gestión de Personal

Sistema web completo para la gestión del personal de una fundación. Incluye gestión de usuarios, expedientes (documentos PDF) con compartición, y un sistema de procesos tipo Task Manager.

## 🛠 Tecnologías

| Componente        | Tecnología                                       |
| ----------------- | ------------------------------------------------ |
| **Backend**       | FastAPI + SQLAlchemy + Pydantic v2               |
| **Frontend**      | React + Vite + React Router                      |
| **Base de datos** | PostgreSQL 14+                                   |
| **Autenticación** | JWT (python-jose) + bcrypt                       |
| **Validaciones**  | RFC, CURP, Email (con validación cruzada)        |
| **API Postal**    | zippopotam.us (autocompletado por código postal) |

---

## 📦 Estructura del Proyecto

```
xolix.3.0/
├── app/                          # Backend FastAPI
│   ├── main.py                   # App principal
│   ├── config.py                 # Configuración (.env)
│   ├── database.py               # SQLAlchemy engine
│   ├── security.py               # JWT + bcrypt
│   ├── dependencies.py           # get_db, get_current_user, require_role
│   ├── models/                   # Modelos SQLAlchemy
│   │   ├── user.py
│   │   ├── expediente.py
│   │   └── proceso.py
│   ├── schemas/                  # Schemas Pydantic
│   │   ├── user.py
│   │   ├── expediente.py
│   │   └── proceso.py
│   ├── routers/                  # Endpoints API
│   │   ├── auth.py               # POST /api/auth/login
│   │   ├── users.py              # CRUD /api/usuarios/
│   │   ├── expedientes.py        # Archivos + compartición
│   │   ├── procesos.py           # Task manager
│   │   └── sepomex.py            # Autocompletado CP
│   ├── services/                 # Lógica de negocio
│   │   ├── user_service.py
│   │   ├── expediente_service.py
│   │   └── proceso_service.py
│   └── validators/               # Validaciones mexicanas
│       └── mexican_ids.py        # RFC, CURP
├── frontend/                     # React + Vite
│   ├── src/
│   │   ├── pages/                # Login, Dashboard, Register, etc.
│   │   ├── components/           # Topbar, Modal, ProtectedRoute
│   │   ├── context/              # AuthContext
│   │   └── api/                  # Cliente API centralizado
│   └── vite.config.js
├── tests/                        # Pytest
│   └── test_api.py
├── .env                          # Variables de entorno
└── requirements.txt
```

---

## 🚀 Instalación Paso a Paso

### 1. Requisitos previos

- Python 3.10+
- PostgreSQL 14+
- Node.js 18+ y npm

### 2. Clonar el repositorio

```bash
git clone <url-del-repositorio>
cd xolix.3.0
```

### 3. Crear la base de datos PostgreSQL

```sql
-- Conectar a PostgreSQL:
psql -U postgres

-- Crear la base de datos:
CREATE DATABASE proyecto_escom;
\q
```

### 4. Configurar variables de entorno

Edita el archivo `.env` en la raíz del proyecto:

```env
DATABASE_URL=postgresql://postgres:TU_CONTRASEÑA@localhost:5432/proyecto_escom
SECRET_KEY=cambia_esta_clave_en_produccion
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

### 5. Backend — Entorno virtual y dependencias

```bash
python -m venv venv

# Windows:
.\venv\Scripts\activate

# Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

### 6. Ejecutar el backend

```bash
python -m uvicorn app.main:app --reload
```

El servidor estará en: http://localhost:8000

### 7. Frontend — Instalar y ejecutar

```bash
cd frontend
npm install
npm run dev
```

El frontend estará en: http://localhost:5173

### 8. Crear el primer usuario (Director)

Como la base de datos inicia vacía y el registro requiere autenticación, crea el primer director directamente en PostgreSQL:

```bash
psql -U postgres -d proyecto_escom
```

```sql
-- Contraseña: admin123 (hasheada con bcrypt)
INSERT INTO users (
    nombre_completo, rfc, curp, sexo, fecha_nacimiento,
    edad, direccion, tipo_personal, rol, correo, password, activo
) VALUES (
    'Administrador Sistema',
    'ADMI850101AAA',
    'ADMI850101HDFRRL09',
    'M', '1985-01-01',
    41, 'ESCOM IPN, Ciudad de México',
    'empleado', 'director',
    'director@xolix.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewKyNAR6mWzZWxam',
    true
);
\q
```

**Credenciales de prueba:**

- Correo: `director@xolix.com`
- Contraseña: `admin123`

---

## 📋 Flujo del Sistema

| Pantalla    | Ruta           | Descripción                         |
| ----------- | -------------- | ----------------------------------- |
| Login       | `/`            | Inicio de sesión                    |
| Dashboard   | `/dashboard`   | Panel principal con accesos rápidos |
| Registro    | `/registro`    | Registrar nuevo personal            |
| Detalle     | `/usuario/:id` | Ver datos completos                 |
| Editar      | `/editar/:id`  | Modificar datos                     |
| Expedientes | `/expedientes` | Gestión de archivos PDF             |
| Procesos    | `/procesos`    | Task manager con subtareas          |

### Permisos por rol

| Acción             | Director | Coordinador | Otros |
| ------------------ | -------- | ----------- | ----- |
| Ver listado        | ✅       | ✅          | ✅    |
| Registrar personal | ✅       | ✅          | ❌    |
| Editar / Eliminar  | ✅       | ✅          | ❌    |
| Expedientes        | ✅       | ✅          | ✅    |
| Procesos           | ✅       | ✅          | ✅    |

---

## 🧪 Tests

```bash
python -m pytest tests/ -v
```

---

## 📡 API (Documentación automática)

Con el servidor corriendo:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### Endpoints principales

| Método   | Ruta                                  | Descripción             |
| -------- | ------------------------------------- | ----------------------- |
| `POST`   | `/api/auth/login`                     | Login con JWT           |
| `GET`    | `/api/usuarios/`                      | Listar usuarios         |
| `POST`   | `/api/usuarios/`                      | Crear usuario           |
| `PUT`    | `/api/usuarios/{id}`                  | Actualizar usuario      |
| `DELETE` | `/api/usuarios/{id}`                  | Eliminar usuario        |
| `GET`    | `/api/sepomex/cp/{cp}`                | Autocompletado por CP   |
| `POST`   | `/api/expedientes/`                   | Subir expediente        |
| `GET`    | `/api/expedientes/propios`            | Mis expedientes         |
| `GET`    | `/api/expedientes/compartidos`        | Expedientes compartidos |
| `POST`   | `/api/expedientes/{id}/compartir`     | Compartir expediente    |
| `POST`   | `/api/procesos/`                      | Crear proceso           |
| `GET`    | `/api/procesos/`                      | Mis procesos            |
| `POST`   | `/api/procesos/{id}/subtareas`        | Agregar subtarea        |
| `PATCH`  | `/api/procesos/subtareas/{id}/toggle` | Toggle subtarea         |

## EjecutarBackend

```bash
venv\Scripts\activate
venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

## Ejecutar Frontend

```bash
cd frontend
npm run dev
```
