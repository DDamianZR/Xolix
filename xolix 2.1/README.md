# XOLIX — Sistema de Gestión de Personal

Sistema web para la gestión del personal de una fundación. Desarrollado con **FastAPI + PostgreSQL + HTML/CSS/JS**.

---

## Requisitos previos

- Linux (Ubuntu/Debian recomendado)
- Python 3.10+
- PostgreSQL 14+

---

## 1. Instalación de PostgreSQL

```bash
sudo apt update
sudo apt install postgresql postgresql-contrib -y
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

Crear la base de datos:

```bash
sudo -u postgres psql
```

Dentro de psql ejecutar:

```sql
CREATE DATABASE proyecto_escom;
\q
```

---

## 2. Clonar / copiar el proyecto

Coloca todos los archivos en una carpeta, por ejemplo `~/xolix/`.

La estructura debe ser:

```
xolix/
├── main.py
├── database.py
├── models.py
├── schemas.py
├── crud.py
├── security.py
├── requirements.txt
├── README.md
└── static/
    ├── style.css
    ├── login.html
    ├── registro.html
    ├── dashboard.html
    ├── detalle.html
    └── editar.html
```

---

## 3. Entorno virtual e instalación de dependencias

```bash
cd ~/xolix
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## 4. Configuración de la base de datos

En el archivo `database.py` ajusta la URL si tu usuario o contraseña de PostgreSQL es diferente:

```python
DATABASE_URL = "postgresql://postgres:TU_CONTRASEÑA@localhost:5432/proyecto_escom"
```

O bien usa una variable de entorno (recomendado):

```bash
export DATABASE_URL="postgresql://postgres:12345@localhost:5432/proyecto_escom"
```

---

## 5. Ejecutar el servidor

```bash
source venv/bin/activate   # si no está activo
uvicorn main:app --reload
```

Abrir en el navegador: [http://localhost:8000](http://localhost:8000)

---

## 6. Primer usuario (Director)

Como la base de datos inicia vacía y el registro requiere autenticación, crea el primer director directamente en PostgreSQL:

```bash
sudo -u postgres psql -d proyecto_escom
```

```sql
-- Contraseña: admin123 (ya hasheada con bcrypt)
INSERT INTO users (nombre_completo, rfc, curp, sexo, edad, direccion, tipo_personal, rol, correo, password)
VALUES (
  'Administrador Sistema',
  'AAAA000000AAA',
  'AAAA000000AAAAAA00',
  'M', 30,
  'ESCOM IPN, Ciudad de México',
  'empleado',
  'director',
  'director@xolix.com',
  '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewKyNAR6mWzZWxam'
);
\q
```

Credenciales de prueba:
- **Correo:** `director@xolix.com`
- **Contraseña:** `admin123`

---

## 7. Flujo del sistema

| Pantalla | Ruta | Descripción |
|---|---|---|
| Login | `/` | Inicio de sesión |
| Dashboard | `/dashboard` | Listado de todo el personal |
| Detalle | `/usuario/{id}` | Ver datos completos de un usuario |
| Editar | `/editar/{id}` | Modificar datos (director/coordinador) |
| Registro | `/registro` | Registrar nuevo personal (director/coordinador) |

### Permisos por rol

| Acción | Director | Coordinador | Otros roles |
|---|---|---|---|
| Ver listado | ✅ | ✅ | ✅ |
| Ver detalle | ✅ | ✅ | ✅ |
| Registrar personal | ✅ | ✅ | ❌ |
| Editar datos | ✅ | ✅ | ❌ |
| Revocar/activar acceso | ✅ | ✅ | ❌ |
| Eliminar usuario | ✅ | ✅ | ❌ |

---

## 8. API (documentación automática)

Con el servidor corriendo, visita:

- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)
