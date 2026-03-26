# Guía para Ejecutar Xolix 3.0 con Docker 🚀

¡Hola! Esta guía te ayudará a levantar todo el sistema Xolix 3.0 de manera instantánea en tu computadora, sin necesidad de configurar Python, Node.js ni bases de datos PostgreSQL manualmente. Todo está empaquetado en contenedores de Docker.

## Prerrequisitos

1. Tener instalado [Docker Desktop](https://www.docker.com/products/docker-desktop/) en tu sistema.
2. Tener instalado `git`.

---

## Instrucciones Paso a Paso

### 1. Clonar el Repositorio
Abre tu terminal y clona el proyecto desde GitHub:
```bash
git clone https://github.com/DDamianZR/Xolix.git
cd Xolix
```

### 2. Levantar los Contenedores
Ejecuta el siguiente comando en la raíz del proyecto (donde está el archivo `docker-compose.yml`):
```bash
docker compose up --build
```
*Nota: La primera vez puede tardar un par de minutos mientras descarga las imágenes (Python, Node, Nginx, PostgreSQL) y compila el panel de React.*

### 3. ¡Acceder al Sistema!
Una vez que veas en la terminal que los servicios están listos, abre tu navegador web y entra a:
👉 [http://localhost](http://localhost)

El sistema iniciará con una base de datos ya pre-cargada con la información que Damián ha establecido (gracias al archivo `init_db.sql`).

---

## Detalles Técnicos
- **Frontend**: Está alojado en el puerto `80` por defecto. Nginx se encarga de servir el build estático y actuar como rev-proxy.
- **Backend (API)**: FastAPI corre en el puerto `8000`. No necesitas acceder directamente, Nginx lo redirige automáticamente en la ruta `/api/`.
- **Base de Datos**: PostgreSQL expone el puerto `5432` con usuario `postgres` y clave `12345`.

*Si deseas apagar el sistema, presiona `Ctrl + C` en la terminal, o ejecuta `docker compose down`.*
