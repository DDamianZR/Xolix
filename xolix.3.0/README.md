# 🟣 XOLIX — Sistema de Gestión para Fundación

Sistema web completo para una fundación que atiende Niñas, Niños y Adolescentes (NNA) que han sufrido vulneración de derechos. Incluye módulos de gestión de usuarios, expedientes (documentos PDF), procesos tipo Task Manager, gestión de casos, y el **Módulo de Protección NNA** con Familiograma interactivo.

## 🛠 Tecnologías

| Componente        | Tecnología                                       |
| ----------------- | ------------------------------------------------ |
| **Backend**       | FastAPI + SQLAlchemy + Pydantic v2               |
| **Frontend**      | React 18 + Vite + React Router v6                |
| **Base de datos** | PostgreSQL 14+                                   |
| **Autenticación** | JWT (python-jose) + bcrypt                       |
| **Grafos**        | @xyflow/react (Familiograma interactivo)         |
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
│   ├── models/
│   │   ├── user.py
│   │   ├── expediente.py
│   │   ├── proceso.py
│   │   ├── caso.py
│   │   └── nna.py                    # CasoNNA, PersonaFamiliar, Familiograma,
│   │                                 #   HistorialFamiliograma, RelacionFamiliar
│   ├── schemas/
│   │   ├── user.py, expediente.py, proceso.py, caso.py
│   │   └── nna.py
│   ├── routers/
│   │   ├── auth.py, users.py, expedientes.py, procesos.py, casos.py
│   │   └── nna.py                    # /api/nna/... (15+ endpoints)
│   ├── services/
│   │   ├── user_service.py, expediente_service.py, proceso_service.py
│   │   ├── caso_service.py
│   │   └── nna_service.py
│   └── validators/
│       └── mexican_ids.py
├── frontend/
│   └── src/
│       ├── pages/nna/
│       │   ├── NnaDashboard.jsx, NuevoCasoNNA.jsx
│       │   ├── CasoNNADetalle.jsx      # Hub de módulos
│       │   ├── EntrevistaWizard.jsx
│       │   ├── FamiliogramaEditor.jsx  # Canvas ReactFlow interactivo
│       │   ├── ObservacionesPage.jsx, PlanAccionPage.jsx
│       │   ├── PersonasFamiliaresPage.jsx   ★ Iteración 2
│       │   ├── RelacionesFamiliaresPage.jsx ★ Iteración 2
│       │   ├── HistorialFamiliogramaPage.jsx ★ Iteración 2
│       │   ├── FamiliogramaReportPage.jsx    ★ Iteración 2
│       │   └── ResumenCasoNNAPage.jsx         ★ Iteración 2
│       ├── components/, context/
│       └── api/client.js             # Cliente API centralizado (JWT auto)
├── migrations/
│   ├── init_db.sql, create_nna.sql
│   ├── create_familiograma_extended.sql  ★ Nuevas tablas iteración 2
│   └── seed_familiograma.sql             ★ Datos de prueba
├── tests/
├── retrospectiva.md                  ★ Retrospectiva del sprint
├── coevaluacion.md                   ★ Evaluación del equipo
├── .env
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


---

## Migraciones Iteración 2 (Familiograma)

Ejecutar después de init_db.sql y create_nna.sql:

    psql -U postgres -d proyecto_escom -f migrations/create_familiograma_extended.sql
    psql -U postgres -d proyecto_escom -f migrations/seed_familiograma.sql

## Migraciones v3.1 — Módulos completos (RF-002 a RF-010)

Ejecutar después de los pasos anteriores:

    psql -U postgres -d proyecto_escom -f migrations/create_full_v2.sql
    psql -U postgres -d proyecto_escom -f migrations/seed_full.sql

Nuevas dependencias Python (instalar):

    pip install reportlab==4.2.2 openpyxl==3.1.4

## Módulos implementados en v3.1

| Módulo | RF | Descripción |
|---|---|---|
| Tutor NNA | RF-002 | Datos del tutor/responsable legal |
| Datos Médicos | RF-002 | Historial, alergias, vacunación |
| Catálogo Derechos | RF-006 | 8 derechos + indicadores cargados |
| Actores | RF-003/004 | CRUD + búsqueda por filtros |
| Diagnóstico | RF-005/006/007 | 4 tipos + derechos vulnerados automáticos |
| Planes de Restitución | RF-008/009/010 | Planes + medidas + seguimientos |
| Auditoría | RNF-004 | AuditLog activo en servicios clave |
| Exportación PDF | RNF-007 | Casos y diagnósticos individuales |
| Exportación Excel | RNF-008 | Casos NNA y actores |
| Reportes | RF-007 | Indicadores globales + evolución mensual |

## Nuevas rutas frontend v3.1

  /actores                           Catálogo de actores con filtros
  /actores/nuevo                     Crear nuevo actor
  /actores/:id                       Detalle del actor
  /actores/:id/editar                Editar actor
  /reportes                          Reportes e indicadores globales
  /nna/casos/:id/diagnostico         Módulo de diagnóstico del caso
  /nna/casos/:id/planes              Planes de restitución + seguimiento

## Nuevos endpoints API v3.1

  GET/POST   /api/catalogo/derechos       Catálogo de derechos
  GET/POST   /api/catalogo/indicadores    Indicadores por derecho
  GET/POST   /api/actores/               Actores (con filtros de búsqueda)
  GET/POST   /api/diagnosticos/          Diagnósticos
  GET/POST   /api/planes/               Planes de restitución
  POST       /api/planes/medidas/:id/seguimientos
  GET        /api/reportes/indicadores    Estadísticas globales
  GET        /api/reportes/derechos-vulnerados
  GET        /api/reportes/exportar/casos/pdf
  GET        /api/reportes/exportar/casos/excel
  GET        /api/reportes/exportar/actores/excel
  GET        /api/nna/casos/:id/tutor    Tutor del caso
  GET        /api/nna/casos/:id/datos-medicos
