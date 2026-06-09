# 2. DISEÑO ARQUITECTÓNICO

---

## 2.1 Objetivo de la Arquitectura

La arquitectura de Xolix 3.0 ha sido diseñada para satisfacer los siguientes atributos de calidad, derivados directamente de los requisitos no funcionales del sistema:

### 2.1.1 Mantenibilidad

**Objetivo:** el sistema debe poder modificarse para corregir defectos, agregar funcionalidades o adaptarse a nuevos requerimientos con un costo de cambio mínimo.

**Decisiones arquitectónicas:**
- Separación estricta en capas (Presentación → Servicios → Persistencia). Un cambio en la base de datos no afecta la lógica de negocio; un cambio en la interfaz no afecta los servicios.
- Cada módulo de negocio (Expedientes, Diagnósticos, Actores, Planes) tiene su propio conjunto de modelos, schemas, servicios y routers. Un error en el módulo de Diagnósticos no propaga cambios al módulo de Planes.
- El uso de Pydantic para la validación centraliza las reglas de validación en un único lugar, facilitando su localización y modificación.

### 2.1.2 Escalabilidad

**Objetivo:** el sistema debe poder atender un número creciente de usuarios y volumen de datos sin necesidad de rediseño.

**Decisiones arquitectónicas:**
- **Escalabilidad horizontal del backend:** FastAPI es una aplicación ASGI sin estado. Múltiples instancias pueden ejecutarse en paralelo detrás de un proxy reverso (Nginx) o balanceador de carga, ya que el estado de sesión se gestiona mediante JWT, no mediante sesiones en servidor.
- **Pool de conexiones:** SQLAlchemy gestiona un pool de conexiones a PostgreSQL, evitando la sobrecarga de establecer una nueva conexión por cada petición.
- **Separación de frontend y backend:** el servidor de React/Vite puede servirse desde una CDN sin escalar el backend.

### 2.1.3 Disponibilidad

**Objetivo:** el sistema debe estar disponible durante las horas laborales de la fundación con un tiempo de recuperación ante fallas bajo.

**Decisiones arquitectónicas:**
- La arquitectura permite despliegue en contenedores (Docker), facilitando reinicio automático ante fallas.
- PostgreSQL soporta replicación para alta disponibilidad.
- Las migraciones de base de datos son versionadas, permitiendo rollback controlado.

### 2.1.4 Seguridad

**Objetivo:** el acceso a la información de los NNA debe estar estrictamente controlado por identidad y rol.

**Decisiones arquitectónicas:**
- **Autenticación JWT:** todos los endpoints (excepto `/api/auth/login`) requieren un token válido. El token tiene tiempo de expiración configurable.
- **Control de acceso basado en roles (RBAC):** el decorador `require_role(*roles)` en FastAPI verifica el rol del usuario antes de procesar cualquier operación.
- **Validación de entrada en múltiples capas:** Pydantic valida en la capa de API; SQLAlchemy aplica restricciones en la capa de persistencia (NOT NULL, UNIQUE, FK).
- **Contraseñas con bcrypt:** las contraseñas se almacenan como hash irreversible. Nunca se almacenan en texto plano.
- **Auditoría activa:** cada operación de escritura (crear, modificar, eliminar) se registra en `audit_logs` con el ID del usuario, la acción y los datos afectados.

### 2.1.5 Modularidad

**Objetivo:** el sistema debe poder extenderse con nuevos módulos sin afectar los existentes.

**Decisiones arquitectónicas:**
- Los módulos se registran en `main.py` mediante `app.include_router()`. Agregar un nuevo módulo requiere únicamente crear sus archivos de modelo/schema/servicio/router y registrarlo.
- El catálogo de derechos e indicadores es independiente de los módulos que lo consumen (Diagnósticos, Planes), comunicándose mediante IDs.

### 2.1.6 Rendimiento

**Objetivo:** las páginas deben cargarse en menos de 3 segundos bajo carga normal; las consultas de listado en menos de 1 segundo.

**Decisiones arquitectónicas:**
- Índices en columnas de búsqueda frecuente (`caso_nna_id`, `responsable_id`, `estado`).
- Paginación disponible en todos los endpoints de listado para limitar el volumen de datos transferidos.
- React con Vite produce bundles optimizados con code splitting automático.
- Los endpoints de exportación (PDF/Excel) usan `StreamingResponse` para no bloquear el servidor durante la generación.

---

## 2.2 Diagrama Arquitectónico

### 2.2.1 Diagrama de Componentes UML 2.x

```
@startuml Xolix_Arquitectura_Componentes

skinparam componentStyle uml2
skinparam backgroundColor #FAFAFA
skinparam component {
  BackgroundColor #E8F4FD
  BorderColor #2980B9
}

title Diagrama de Componentes — Xolix 3.0\nArquitectura en Capas con API REST

' ─────────────── CAPA DE PRESENTACIÓN ───────────────
package "Capa de Presentación [React 18 + Vite]" <<layer>> {
  [LoginPage]             <<boundary>>
  [Dashboard]             <<boundary>>
  [NnaDashboard]          <<boundary>>
  [CasoNNADetalle]        <<boundary>>
  [EntrevistaWizard]      <<boundary>>
  [FamiliogramaEditor]    <<boundary>>
  [DiagnosticoPage]       <<boundary>>
  [PlanesPage]            <<boundary>>
  [ActoresList]           <<boundary>>
  [ReportesPage]          <<boundary>>
  [APIClient]             <<facade>>
}

' ─────────────── CAPA DE API / CONTROLADORES ─────────────────
package "Capa API REST [FastAPI 0.111]" <<layer>> {
  [Router Auth]      <<controller>>
  [Router Usuarios]  <<controller>>
  [Router NNA]       <<controller>>
  [Router Catalogo]  <<controller>>
  [Router Actores]   <<controller>>
  [Router Diagnosticos] <<controller>>
  [Router Planes]    <<controller>>
  [Router Reportes]  <<controller>>

  package "Middleware" {
    [JWT Middleware]       <<interceptor>>
    [RBAC Dependency]     <<interceptor>>
    [CORS Middleware]     <<interceptor>>
  }
}

' ─────────────── CAPA DE SERVICIOS / LÓGICA DE NEGOCIO ─────────
package "Capa de Servicios [Python 3.12]" <<layer>> {
  [UserService]          <<service>>
  [NNAService]           <<service>>
  [CatalogoService]      <<service>>
  [ActorService]         <<service>>
  [DiagnosticoService]   <<service>>
  [PlanService]          <<service>>
  [ExportService]        <<service>>
  [ExtrasService]        <<service>>
}

' ─────────────── CAPA ORM / REPOSITORIO ─────────────────────
package "Capa ORM [SQLAlchemy 2.0]" <<layer>> {
  [ORMUser]          <<entity>>
  [ORMCasoNNA]       <<entity>>
  [ORMTutorNNA]      <<entity>>
  [ORMDatosMedicos]  <<entity>>
  [ORMFamiliograma]  <<entity>>
  [ORMDerecho]       <<entity>>
  [ORMActor]         <<entity>>
  [ORMDiagnostico]   <<entity>>
  [ORMPlan]          <<entity>>
  [ORMAuditLog]      <<entity>>
  [SessionFactory]   <<infrastructure>>
}

' ─────────────── CAPA DE BASE DE DATOS ──────────────────────
package "Capa de Persistencia [PostgreSQL 18]" <<layer>> {
  database "proyecto_escom" as DB {
    [users]
    [nna_casos]
    [nna_tutores]
    [nna_datos_medicos]
    [nna_familiogramas]
    [derechos]
    [actores]
    [diagnosticos]
    [planes_restitucion]
    [audit_logs]
    [-- 27 tablas adicionales --]
  }
}

' ─────────────── COMPONENTES EXTERNOS ──────────────────────
package "Servicios Externos" {
  [zippopotam.us API]  <<external>>
  [reportlab]          <<library>>
  [openpyxl]           <<library>>
  [bcrypt]             <<library>>
  [python-jose]        <<library>>
}

' ─────────────── DEPENDENCIAS ──────────────────────────────

[APIClient] --> [Router Auth]        : HTTP/REST (JWT)
[APIClient] --> [Router NNA]         : HTTP/REST (JWT)
[APIClient] --> [Router Actores]     : HTTP/REST (JWT)
[APIClient] --> [Router Diagnosticos]: HTTP/REST (JWT)
[APIClient] --> [Router Planes]      : HTTP/REST (JWT)
[APIClient] --> [Router Reportes]    : HTTP/REST (JWT)

[LoginPage] --> [APIClient]
[NnaDashboard] --> [APIClient]
[FamiliogramaEditor] --> [APIClient]
[DiagnosticoPage] --> [APIClient]
[PlanesPage] --> [APIClient]
[ActoresList] --> [APIClient]
[ReportesPage] --> [APIClient]

[Router Auth]         --> [JWT Middleware]
[Router NNA]          --> [RBAC Dependency]
[Router Diagnosticos] --> [RBAC Dependency]

[Router Auth]         --> [UserService]
[Router NNA]          --> [NNAService]
[Router Catalogo]     --> [CatalogoService]
[Router Actores]      --> [ActorService]
[Router Diagnosticos] --> [DiagnosticoService]
[Router Planes]       --> [PlanService]
[Router Reportes]     --> [ExportService]

[UserService]        --> [ORMUser]
[NNAService]         --> [ORMCasoNNA]
[NNAService]         --> [ORMTutorNNA]
[NNAService]         --> [ORMDatosMedicos]
[DiagnosticoService] --> [ORMDiagnostico]
[DiagnosticoService] --> [ORMDerecho]
[PlanService]        --> [ORMPlan]
[ExtrasService]      --> [ORMAuditLog]

[ORMCasoNNA]    --> [SessionFactory]
[ORMDiagnostico]--> [SessionFactory]
[ORMPlan]       --> [SessionFactory]
[SessionFactory]--> DB

[JWT Middleware]  --> [python-jose]
[UserService]     --> [bcrypt]
[ExportService]   --> [reportlab]
[ExportService]   --> [openpyxl]
[Router Auth]     --> [zippopotam.us API] : HTTP (sepomex)

@enduml
```

### 2.2.2 Diagrama de Despliegue UML 2.x

```
@startuml Xolix_Despliegue

skinparam nodeStyle uml2
skinparam backgroundColor #FAFAFA

title Diagrama de Despliegue — Xolix 3.0\nEntorno de Desarrollo Local

node "Estación de Trabajo\n[Windows 11]" as WS {
  node "Navegador Web\n[Chrome / Firefox]" as Browser {
    artifact "React SPA\n[xolix-frontend.js]" as SPA
  }
  
  node "Servidor Frontend\n[Node.js + Vite Dev Server\npuerto 5173]" as FrontendServer {
    artifact "Frontend Bundle\n[React 18 + JSX]" as FrontendApp
  }
  
  node "Servidor Backend\n[Python 3.12 + Uvicorn\npuerto 8000]" as BackendServer {
    artifact "FastAPI App\n[app.main:app]" as FastAPIApp
    artifact "SQLAlchemy ORM\n[engine + session]" as ORM
  }
  
  node "Servidor de Base de Datos\n[PostgreSQL 18\npuerto 5432]" as DBServer {
    database "proyecto_escom" as DB {
      artifact "37 tablas relacionales" as Tables
    }
  }
}

node "API Externa\n[zippopotam.us]" as ExtAPI

Browser     --> FrontendServer : HTTP :5173
Browser     --> BackendServer  : REST API :8000 (JSON + JWT)
FrontendServer --> FrontendApp
BackendServer  --> FastAPIApp
FastAPIApp     --> ORM
ORM            --> DB           : SQL (psycopg2)
FastAPIApp     --> ExtAPI       : HTTP (código postal)

@enduml
```

---

## 2.3 Explicación de la Arquitectura

### 2.3.1 Capa de Presentación (Frontend)

**Tecnología:** React 18 con Vite 5, React Router v6, @xyflow/react.

**Responsabilidades:**
- Renderizar la interfaz de usuario en el navegador del usuario.
- Gestionar el estado local de la aplicación (useState, useEffect).
- Realizar peticiones HTTP a la API REST a través del cliente centralizado `src/api/client.js`.
- Almacenar el JWT en `localStorage` y adjuntarlo en el encabezado `Authorization: Bearer` de cada petición.
- Gestionar la navegación entre módulos mediante React Router.

**Componentes principales:**
- `pages/`: páginas completas, una por funcionalidad principal.
- `components/`: componentes reutilizables (Topbar, formularios, tarjetas).
- `api/client.js`: abstracción del cliente HTTP con gestión automática de token.
- `context/`: contexto React para el estado global del usuario autenticado.

**Dependencias de entrada:** ninguna (es la capa más externa).
**Dependencias de salida:** únicamente la API REST del backend.

### 2.3.2 Capa de API REST (Backend — Routers FastAPI)

**Tecnología:** FastAPI 0.111 sobre ASGI (Uvicorn).

**Responsabilidades:**
- Exponer los endpoints HTTP de la API REST.
- Validar la estructura y tipos de los datos de entrada mediante schemas Pydantic.
- Verificar la autenticación (JWT válido) y la autorización (rol requerido) en cada endpoint.
- Deserializar las peticiones y serializar las respuestas en JSON.
- Delegar la ejecución de la lógica de negocio a la capa de servicios.

**Restricciones:**
- Los routers NO ejecutan lógica de negocio directamente. Solo llaman a funciones de la capa de servicios.
- Los routers NO acceden directamente a la base de datos. Toda la persistencia pasa por SQLAlchemy a través de los servicios.

**Middleware aplicado:**
- `CORSMiddleware`: permite peticiones desde `http://localhost:5173` (frontend de desarrollo).
- `JWT Middleware`: verifica el token en cada petición mediante `get_current_user()`.
- `RBAC Dependency`: verifica el rol del usuario mediante `require_role(*roles)`.

### 2.3.3 Capa de Servicios (Lógica de Negocio)

**Tecnología:** Python 3.12 puro (sin dependencias de framework).

**Responsabilidades:**
- Implementar las reglas de negocio del dominio.
- Orquestar operaciones que involucran múltiples entidades (ejemplo: crear un diagnóstico genera automáticamente los registros de derechos vulnerados).
- Gestionar transacciones de base de datos (commit/rollback).
- Registrar las acciones en el log de auditoría.

**Restricciones:**
- Los servicios NO importan nada de FastAPI (ni Request, ni Response, ni HTTPException en algunas versiones).
- Los servicios reciben la sesión de BD como parámetro (`db: Session`), nunca la crean directamente.

### 2.3.4 Capa ORM / Repositorio (SQLAlchemy)

**Tecnología:** SQLAlchemy 2.0 con driver psycopg2.

**Responsabilidades:**
- Mapear las clases Python a tablas de PostgreSQL mediante el patrón Active Record.
- Gestionar el pool de conexiones a la base de datos.
- Traducir las operaciones de Python (consultas, inserciones) a SQL.
- Gestionar las relaciones entre entidades mediante `relationship()`.

**Restricciones:**
- Los modelos ORM NO contienen lógica de negocio compleja (solo validaciones simples del dominio).
- Las tablas se crean automáticamente con `Base.metadata.create_all(bind=engine)` al iniciar la aplicación.

### 2.3.5 Capa de Persistencia (PostgreSQL)

**Tecnología:** PostgreSQL 18.

**Responsabilidades:**
- Almacenar todos los datos del sistema de forma persistente y con integridad referencial.
- Ejecutar las consultas SQL generadas por SQLAlchemy.
- Aplicar restricciones de integridad (PK, FK, NOT NULL, UNIQUE, CHECK).
- Gestionar la concurrencia mediante transacciones ACID.

**Base de datos:** `proyecto_escom` con 37 tablas relacionales.

---

## 2.4 Beneficios y Limitaciones

### 2.4.1 Beneficios de la Arquitectura

| Beneficio | Descripción |
|---|---|
| **Desacoplamiento total frontend/backend** | El frontend y el backend pueden desplegarse, escalarse y desarrollarse de forma completamente independiente. El contrato es únicamente la API REST documentada con OpenAPI/Swagger. |
| **Documentación automática de la API** | FastAPI genera automáticamente la documentación Swagger UI (`/docs`) y ReDoc (`/redoc`) a partir del código. |
| **Tipado fuerte en dos lenguajes** | Python con Pydantic + TypeScript (opcional) en el frontend proporciona validación de tipos en tiempo de ejecución y en compilación. |
| **Rapidez de desarrollo** | FastAPI reduce significativamente el boilerplate comparado con Django REST Framework o Flask. |
| **Testabilidad** | La inyección de dependencias de FastAPI facilita reemplazar la sesión de BD por una de prueba sin modificar el código de producción. |
| **Extensibilidad modular** | Agregar un nuevo módulo de negocio requiere únicamente crear los archivos correspondientes y registrar el router. No se modifican archivos existentes. |

### 2.4.2 Limitaciones de la Arquitectura

| Limitación | Descripción | Mitigación |
|---|---|---|
| **Sin caché distribuido** | No hay Redis u otro sistema de caché. Consultas frecuentes (catálogo de derechos, lista de actores) se ejecutan contra la BD en cada petición. | Agregar Redis en iteraciones futuras para caché de catálogos. |
| **Sin búsqueda full-text optimizada** | Las búsquedas de texto usan `ILIKE` de PostgreSQL, que no escala bien con millones de registros. | Integrar PostgreSQL Full Text Search o Elasticsearch en versiones futuras. |
| **Sin WebSockets** | Las notificaciones en tiempo real (por ejemplo, cuando se actualiza el estado de un caso) requieren polling del frontend. | Implementar Server-Sent Events o WebSockets con FastAPI en versiones futuras. |
| **JWT sin revocación** | Un JWT emitido es válido hasta su expiración incluso si el usuario cambia su contraseña o es desactivado. | Implementar una lista negra de tokens (blacklist) en Redis en versiones futuras. |
| **SQLite no compatible** | El sistema está diseñado específicamente para PostgreSQL (usa tipos JSON, ENUM nativos). No puede migrarse trivialmente a SQLite o MySQL. | Esta limitación es aceptable dado el entorno de despliegue objetivo. |
