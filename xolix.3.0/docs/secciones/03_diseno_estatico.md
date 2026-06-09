# 3. DISEÑO ESTÁTICO

---

## 3.1 Descripción General

El diseño estático de Xolix 3.0 describe la estructura del software: cómo se organizan los componentes, qué clases existen, cómo se relacionan entre sí y cómo se agrupan en paquetes y subsistemas.

El sistema se divide en **seis subsistemas funcionales** que corresponden directamente a los módulos de negocio: Seguridad, Expedientes, Diagnósticos, Planeación, Actores y Familiograma. Cada subsistema opera de forma relativamente independiente, comunicándose a través de interfaces bien definidas.

La estructura sigue el patrón BCE (Boundary-Control-Entity) para organizar las responsabilidades dentro de cada subsistema. Las clases de presentación (Boundary) no conocen los detalles de persistencia; las clases de control (servicios) coordinan sin acoplarse a los detalles de la interfaz; las clases de entidad modelan el dominio sin conocer a sus consumidores.

---

## 3.2 Diseño de Subsistemas

### 3.2.1 Subsistema de Seguridad

**Responsabilidades:**
- Autenticar usuarios mediante usuario y contraseña.
- Generar y validar tokens JWT.
- Verificar el rol del usuario en cada petición (RBAC).
- Registrar intentos de acceso en el log de auditoría.

**Interfaces expuestas:**
- `POST /api/auth/login` → retorna `{access_token, token_type}`
- `GET /api/auth/me` → retorna los datos del usuario autenticado

**Dependencias:**
- Depende del subsistema de Expedientes únicamente para cargar el perfil del usuario.
- Provee autenticación a todos los demás subsistemas mediante la dependencia `get_current_user`.

**Clases participantes:**
- Boundary: `IULogin` (LoginPage.jsx)
- Control: `AccessCtr` (auth.py router + security.py)
- Entity: `ORMUser` (models/user.py)

### 3.2.2 Subsistema de Expedientes

**Responsabilidades:**
- Gestionar el ciclo de vida completo del caso NNA: creación, actualización, cierre.
- Administrar los datos personales, médicos, familiares y del tutor del NNA.
- Gestionar la carga de documentos del expediente.
- Proveer funcionalidades de búsqueda y filtrado de casos.

**Interfaces expuestas:**
- `GET/POST /api/nna/casos` → listar y crear casos
- `GET/PUT /api/nna/casos/{id}` → obtener y actualizar caso
- `GET/PUT /api/nna/casos/{id}/tutor` → gestionar tutor
- `GET/PUT /api/nna/casos/{id}/datos-medicos` → gestionar datos médicos

**Dependencias:**
- Depende del Subsistema de Seguridad para autenticación y roles.
- Provee la entidad `CasoNNA` al Subsistema de Diagnósticos y al de Planeación.

**Clases participantes:**
- Boundary: `IUExpediente` (NuevoCasoNNA.jsx, CasoNNADetalle.jsx)
- Control: `ExpedienteCtr` (nna_service.py, nna.py router)
- Entity: `ORMCasoNNA`, `ORMTutorNNA`, `ORMDatosMedicosNNA`

### 3.2.3 Subsistema de Diagnósticos

**Responsabilidades:**
- Registrar diagnósticos de cuatro tipos: inicial, NNA, tutor y entorno.
- Evaluar indicadores de derechos para cada diagnóstico.
- Generar automáticamente los registros de derechos vulnerados cuando un indicador es marcado como vulnerado.
- Proveer el resumen de derechos vulnerados por caso para su uso en planeación.

**Interfaces expuestas:**
- `GET/POST /api/diagnosticos` → listar y crear diagnósticos
- `GET /api/diagnosticos/{id}` → detalle de diagnóstico
- `GET /api/diagnosticos/caso/{id}/derechos-vulnerados` → resumen por caso

**Dependencias:**
- Depende del Subsistema de Expedientes para la entidad `CasoNNA`.
- Depende del catálogo de `Derecho` e `Indicador`.
- Provee los derechos vulnerados al Subsistema de Planeación.

**Clases participantes:**
- Boundary: `IUDiagnostico` (DiagnosticoPage.jsx)
- Control: `DiagnosticoCtr` (diagnostico_service.py, diagnosticos.py router)
- Entity: `ORMDiagnostico`, `ORMIndicadorDiagnostico`, `ORMDerechoVulnerado`

### 3.2.4 Subsistema de Planeación

**Responsabilidades:**
- Crear planes de restitución con objetivos, responsables y fechas.
- Registrar medidas de restitución de diferentes tipos (psicológica, legal, médica, educativa, social, económica).
- Registrar seguimientos de avance para cada medida.
- Actualizar automáticamente el porcentaje de avance de la medida al registrar seguimientos.

**Interfaces expuestas:**
- `GET/POST /api/planes` → listar y crear planes
- `GET/PUT /api/planes/{id}` → detalle y actualización de plan
- `POST /api/planes/{id}/medidas` → agregar medida
- `POST /api/planes/medidas/{id}/seguimientos` → registrar seguimiento

**Dependencias:**
- Depende del Subsistema de Expedientes para la entidad `CasoNNA`.
- Depende del Subsistema de Diagnósticos para identificar los derechos afectados.
- Depende del Subsistema de Actores para vincular medidas con actores.

**Clases participantes:**
- Boundary: `IUPlan` (PlanesPage.jsx)
- Control: `PlanCtr` (plan_service.py, planes.py router)
- Entity: `ORMPlanRestitucion`, `ORMMedidaRestitucion`, `ORMSeguimientoMedida`

### 3.2.5 Subsistema de Actores

**Responsabilidades:**
- Registrar actores (organizaciones gubernamentales, civiles, empresas, personas físicas).
- Gestionar los datos de contacto, horarios, servicios y requisitos de cada actor.
- Proveer búsqueda de actores por municipio, derecho vulnerado y tipo de servicio.
- Vincular servicios de actores con derechos del catálogo.

**Interfaces expuestas:**
- `GET/POST /api/actores` → listar y crear actores (con filtros de búsqueda)
- `GET/PUT /api/actores/{id}` → detalle y actualización
- `POST /api/actores/{id}/servicios` → agregar servicio

**Dependencias:**
- Depende del Catálogo de Derechos para vincular servicios.
- Es consumido por el Subsistema de Planeación para vincular medidas con actores.

**Clases participantes:**
- Boundary: `IUActor` (ActoresList.jsx, ActorDetalle.jsx, ActorForm.jsx)
- Control: `ActorCtr` (actor_service.py, actores.py router)
- Entity: `ORMActor`, `ORMResponsableActor`, `ORMServicioActor`, `ORMHorarioActor`

### 3.2.6 Subsistema de Familiograma

**Responsabilidades:**
- Registrar personas del entorno familiar del NNA.
- Registrar relaciones entre personas del entorno familiar.
- Gestionar el canvas visual del familiograma mediante ReactFlow.
- Almacenar el grafo como JSON en PostgreSQL.
- Mantener historial de versiones del familiograma.

**Interfaces expuestas:**
- `GET/POST /api/nna/casos/{id}/personas` → personas del caso
- `GET/POST /api/nna/casos/{id}/relaciones` → relaciones familiares
- `GET/PUT /api/nna/casos/{id}/familiograma` → canvas del grafo

**Dependencias:**
- Depende del Subsistema de Expedientes para la entidad `CasoNNA`.

**Clases participantes:**
- Boundary: `IUFamiliograma` (FamiliogramaEditor.jsx, PersonasFamiliaresPage.jsx)
- Control: `FamiliogramaCtr` (nna_service.py — funciones de familiograma)
- Entity: `ORMPersonaFamiliar`, `ORMRelacionFamiliar`, `ORMFamiliograma`

---

## 3.3 Diseño de Módulos

### 3.3.1 Módulo de Autenticación (auth)

| Atributo | Detalle |
|---|---|
| **Objetivo** | Gestionar la identidad de los usuarios del sistema |
| **Entradas** | Credenciales (correo, contraseña) en JSON |
| **Salidas** | Token JWT, datos del perfil del usuario |
| **Dependencias** | `security.py` (hash/verify), `user_service.py`, PostgreSQL tabla `users` |

### 3.3.2 Módulo de Usuarios (users)

| Atributo | Detalle |
|---|---|
| **Objetivo** | Administrar el personal de la fundación (CRUD) |
| **Entradas** | Datos del empleado (nombre, RFC, CURP, rol, etc.) |
| **Salidas** | Perfil de usuario, lista paginada de usuarios |
| **Dependencias** | `auth`, validadores de RFC/CURP, tabla `users` |

### 3.3.3 Módulo de Casos NNA (nna)

| Atributo | Detalle |
|---|---|
| **Objetivo** | Gestionar el expediente completo del NNA |
| **Entradas** | Datos del NNA, tutor, datos médicos, vacunación |
| **Salidas** | Expediente completo, lista de casos por estado |
| **Dependencias** | `auth`, `familiograma`, tablas `nna_casos`, `nna_tutores`, `nna_datos_medicos` |

### 3.3.4 Módulo de Catálogo (catalogo)

| Atributo | Detalle |
|---|---|
| **Objetivo** | Gestionar el catálogo de derechos e indicadores de evaluación |
| **Entradas** | Datos del derecho (nombre, categoría, artículo) e indicadores |
| **Salidas** | Listado de derechos por categoría, indicadores por derecho |
| **Dependencias** | Tablas `derechos`, `indicadores` |

### 3.3.5 Módulo de Actores (actores)

| Atributo | Detalle |
|---|---|
| **Objetivo** | Registrar y localizar organizaciones y personas que pueden apoyar la restitución de derechos |
| **Entradas** | Datos del actor, servicios, horarios, responsables |
| **Salidas** | Directorio de actores filtrable, detalle con servicios y requisitos |
| **Dependencias** | `catalogo` (derechos), tablas `actores`, `actores_servicios`, `actores_horarios` |

### 3.3.6 Módulo de Diagnóstico (diagnosticos)

| Atributo | Detalle |
|---|---|
| **Objetivo** | Documentar la evaluación del NNA, tutor y entorno; identificar derechos vulnerados |
| **Entradas** | Tipo de diagnóstico, evaluación de indicadores, observaciones |
| **Salidas** | Diagnóstico con derechos vulnerados generados automáticamente |
| **Dependencias** | `nna` (caso), `catalogo` (indicadores/derechos), tablas `diagnosticos`, `indicadores_diagnostico`, `derechos_vulnerados` |

### 3.3.7 Módulo de Planes (planes)

| Atributo | Detalle |
|---|---|
| **Objetivo** | Planificar y hacer seguimiento de las medidas de restitución de derechos |
| **Entradas** | Objetivo del plan, medidas (tipo, responsable, actor), seguimientos de avance |
| **Salidas** | Plan con medidas y avances, porcentaje global de cumplimiento |
| **Dependencias** | `nna` (caso), `actores`, `diagnosticos` (derechos afectados), tablas `planes_restitucion`, `medidas_restitucion`, `seguimientos_medida` |

### 3.3.8 Módulo de Reportes (reportes)

| Atributo | Detalle |
|---|---|
| **Objetivo** | Generar indicadores globales, reportes de evolución y exportaciones PDF/Excel |
| **Entradas** | Parámetros de filtrado (fecha, estado, tipo) |
| **Salidas** | KPIs, gráficas de derechos vulnerados, archivos PDF/Excel |
| **Dependencias** | Todos los módulos (consume datos de todas las tablas), `reportlab`, `openpyxl` |

---

## 3.4 Diseño de Paquetes

### 3.4.1 Estructura de Paquetes Backend

```
@startuml Xolix_Paquetes_Backend

skinparam packageStyle rectangle
skinparam backgroundColor #FAFAFA

title Diagrama de Paquetes — Backend Xolix 3.0

package "app" <<module>> {

  package "app.models" <<module>> {
    package "app.models.user"       { class User }
    package "app.models.caso"       { class Caso }
    package "app.models.nna"        { class CasoNNA; class TutorNNA; class DatosMedicosNNA }
    package "app.models.catalogo"   { class Derecho; class Indicador }
    package "app.models.actor"      { class Actor; class ServicioActor }
    package "app.models.diagnostico"{ class Diagnostico; class DerechoVulnerado }
    package "app.models.plan"       { class PlanRestitucion; class MedidaRestitucion }
    package "app.models.extras"     { class AuditLog; class Comentario }
    package "app.models.proceso"    { class Proceso; class Subtarea }
    package "app.models.expediente" { class Expediente }
  }

  package "app.schemas" <<module>> {
    package "app.schemas.user"        { class UserCreate; class UserResponse }
    package "app.schemas.nna"         { class CasoNNACreate; class CasoNNAResponse }
    package "app.schemas.catalogo"    { class DerechoCreate; class DerechoResponse }
    package "app.schemas.actor"       { class ActorCreate; class ActorResponse }
    package "app.schemas.diagnostico" { class DiagnosticoCreate; class DiagnosticoResponse }
    package "app.schemas.plan"        { class PlanCreate; class PlanResponse }
  }

  package "app.services" <<module>> {
    package "app.services.user_service"        { class UserService }
    package "app.services.nna_service"         { class NNAService }
    package "app.services.catalogo_service"    { class CatalogoService }
    package "app.services.actor_service"       { class ActorService }
    package "app.services.diagnostico_service" { class DiagnosticoService }
    package "app.services.plan_service"        { class PlanService }
    package "app.services.export_service"      { class ExportService }
    package "app.services.extras_service"      { class ExtrasService }
  }

  package "app.routers" <<module>> {
    package "app.routers.auth"        { class AuthRouter }
    package "app.routers.users"       { class UsersRouter }
    package "app.routers.nna"         { class NNARouter }
    package "app.routers.catalogo"    { class CatalogoRouter }
    package "app.routers.actores"     { class ActoresRouter }
    package "app.routers.diagnosticos"{ class DiagnosticosRouter }
    package "app.routers.planes"      { class PlanesRouter }
    package "app.routers.reportes"    { class ReportesRouter }
  }

  package "app.validators" <<module>> {
    package "app.validators.mexican_ids" { class MexicanIDValidator }
  }

  package "app.security"     { class SecurityModule }
  package "app.database"     { class DatabaseModule }
  package "app.dependencies" { class DependenciesModule }
  package "app.config"       { class Settings }
  package "app.main"         { class Application }
}

' Dependencias entre paquetes
"app.routers"   ..> "app.services"   : usa
"app.routers"   ..> "app.schemas"    : usa
"app.services"  ..> "app.models"     : usa
"app.services"  ..> "app.database"   : Session
"app.routers"   ..> "app.dependencies": Depends
"app.dependencies" ..> "app.security": verifica JWT
"app.security"  ..> "app.models.user": carga User
"app.main"      ..> "app.routers"    : include_router
"app.main"      ..> "app.models"     : create_all

@enduml
```

### 3.4.2 Descripción de Paquetes Backend

| Paquete | Responsabilidad |
|---|---|
| `app.models` | Definición de las clases SQLAlchemy. Mapeo objeto-relacional. Sin lógica de negocio. |
| `app.schemas` | Clases Pydantic para validación de entrada (Create/Update) y serialización de salida (Response). |
| `app.services` | Implementación de la lógica de negocio. Operaciones CRUD y reglas de dominio. |
| `app.routers` | Definición de endpoints HTTP. Reciben peticiones, validan con schemas y delegan a servicios. |
| `app.validators` | Validadores de datos específicos del dominio mexicano (RFC, CURP). |
| `app.security` | Funciones de hash/verify de contraseñas y creación/verificación de JWT. |
| `app.database` | Configuración del engine SQLAlchemy, SessionFactory y función `get_db`. |
| `app.dependencies` | Funciones de inyección de dependencias reutilizables: `get_current_user`, `require_role`. |
| `app.config` | Clase `Settings` que lee variables de entorno desde `.env` con pydantic-settings. |

### 3.4.3 Estructura de Paquetes Frontend

```
@startuml Xolix_Paquetes_Frontend

skinparam packageStyle rectangle

title Diagrama de Paquetes — Frontend Xolix 3.0

package "src" <<directory>> {

  package "src.pages" <<directory>> {
    package "src.pages.nna" <<directory>> {
      class NnaDashboard
      class NuevoCasoNNA
      class CasoNNADetalle
      class EntrevistaWizard
      class FamiliogramaEditor
      class PersonasFamiliaresPage
      class RelacionesFamiliaresPage
      class DiagnosticoPage
      class PlanesPage
      class ResumenCasoNNAPage
    }
    class LoginPage
    class RegistroPage
    class Dashboard
    class ActoresList
    class ActorDetalle
    class ActorForm
    class ReportesPage
  }

  package "src.components" <<directory>> {
    class Topbar
    class ProtectedRoute
    class StatusBadge
    class ConfirmModal
  }

  package "src.context" <<directory>> {
    class AuthContext
    class UserContext
  }

  package "src.api" <<directory>> {
    class APIClient
  }

  class App
  class main
}

"src.pages"     ..> "src.api"       : HTTP calls
"src.pages"     ..> "src.components": usa
"src.pages"     ..> "src.context"   : consume
"src.context"   ..> "src.api"       : autenticación
"App"           ..> "src.pages"     : rutas
"App"           ..> "src.context"   : Provider

@enduml
```

---

## 3.5 Diseño de Clases

### 3.5.1 Diagrama de Clases de Dominio (Entidades Principales)

```
@startuml Xolix_ClasesDominio

skinparam classBackgroundColor #F0F8FF
skinparam classBorderColor #2C3E50
skinparam classHeaderBackgroundColor #2C3E50
skinparam classHeaderFontColor #FFFFFF

title Diagrama de Clases de Dominio — Xolix 3.0

' ══════════════════════════════════════════
' CLASES DE SEGURIDAD Y USUARIO
' ══════════════════════════════════════════

class User <<entity>> {
  +id: Integer {PK}
  +nombre: String[50]
  +apellido_paterno: String[50]
  +apellido_materno: String[50]
  +rfc: String[13] {UNIQUE}
  +curp: String[18] {UNIQUE}
  +sexo: String[10]
  +fecha_nacimiento: Date
  +edad: Integer
  +estado: String[50]
  +municipio: String[100]
  +colonia: String[100]
  +calle: String[100]
  +numero: String[20]
  +codigo_postal: String[5]
  +tipo_personal: String[20]
  +rol: String[30]
  +correo: String[100] {UNIQUE}
  -password: String[255]
  +activo: Boolean
  +verificado: Boolean
  +foto_perfil: String[500]
  +fecha_creacion: DateTime
  --
  +nombre_completo(): String
  +tiene_rol(rol: String): Boolean
}

enum RolUsuario <<enumeration>> {
  director
  coordinador
  psicologo
  trabajador_social
  legal
  voluntario
}

User --> RolUsuario : tiene

' ══════════════════════════════════════════
' CLASES DE EXPEDIENTE NNA
' ══════════════════════════════════════════

class CasoNNA <<entity>> {
  +id: Integer {PK}
  +nna_nombre: String[200]
  +nna_curp: String[18]
  +nna_fecha_nacimiento: Date
  +nna_edad: Integer
  +nna_genero: GeneroNNA
  +nna_nacionalidad: String[100]
  +nna_estado_civil: String[50]
  +estado: EstadoCasoNNA
  +creador_id: Integer {FK → users}
  +fecha_creacion: DateTime
  +fecha_actualizacion: DateTime
  --
  +calcular_edad(): Integer
  +esta_activo(): Boolean
}

enum GeneroNNA <<enumeration>> {
  masculino
  femenino
  no_binario
  prefiero_no_decir
}

enum EstadoCasoNNA <<enumeration>> {
  activo
  seguimiento
  cerrado
  archivado
}

class TutorNNA <<entity>> {
  +id: Integer {PK}
  +caso_id: Integer {FK → nna_casos}
  +nombre: String[100]
  +apellido_paterno: String[100]
  +apellido_materno: String[100]
  +curp: String[18]
  +rfc: String[13]
  +parentesco: String[50]
  +telefono: String[20]
  +correo: String[100]
  +direccion: String[300]
  +ocupacion: String[150]
  +documento_identificacion: String[50]
  +numero_documento: String[100]
}

class DatosMedicosNNA <<entity>> {
  +id: Integer {PK}
  +caso_id: Integer {FK → nna_casos}
  +historial_medico: Text
  +alergias: Text
  +discapacidades: Text
  +tipo_sangre: String[5]
  +medico_responsable: String[200]
  +institucion_medica: String[200]
  +cartilla_vacunacion: JSON
}

class PersonaFamiliar <<entity>> {
  +id: Integer {PK}
  +caso_id: Integer {FK → nna_casos}
  +nombre: String[200]
  +edad: Integer
  +genero: GeneroNNA
  +rol_en_familia: String[100]
  +tipo_simbolo: TipoSimboloFamiliar
  +observaciones: Text
  +telefono: String[20]
  +direccion: String[300]
  +ocupacion: String[150]
  +escolaridad: String[100]
  +estado_salud: String[200]
  +vive_con_nna: Boolean
  +es_responsable_legal: Boolean
}

enum TipoSimboloFamiliar <<enumeration>> {
  normal
  clave
  cuidador
  agresor
  fallecido
}

class RelacionFamiliar <<entity>> {
  +id: Integer {PK}
  +caso_id: Integer {FK → nna_casos}
  +persona_origen_id: Integer {FK → nna_personas}
  +persona_destino_id: Integer {FK → nna_personas}
  +tipo_relacion: TipoRelacionFamiliar
  +descripcion: String[300]
  +bidireccional: Boolean
}

enum TipoRelacionFamiliar <<enumeration>> {
  biologica
  adoptiva
  acogimiento
  tutela
  conflictiva
  distante
  apoyo
}

class Familiograma <<entity>> {
  +id: Integer {PK}
  +caso_id: Integer {FK → nna_casos}
  +grafo_json: JSON
  +version: Integer
  +fecha_creacion: DateTime
  +fecha_actualizacion: DateTime
  --
  +agregar_nodo(persona: PersonaFamiliar): void
  +agregar_arista(relacion: RelacionFamiliar): void
}

' ══════════════════════════════════════════
' CATÁLOGO
' ══════════════════════════════════════════

class Derecho <<entity>> {
  +id: Integer {PK}
  +nombre: String[200]
  +descripcion: Text
  +categoria: CategoriaDerecho
  +articulo_referencia: String[100]
  +activo: Boolean
}

enum CategoriaDerecho <<enumeration>> {
  salud
  educacion
  identidad
  familia
  proteccion
  participacion
  alimentacion
  vivienda
  otro
}

class Indicador <<entity>> {
  +id: Integer {PK}
  +derecho_id: Integer {FK → derechos}
  +nombre: String[300]
  +descripcion: Text
  +tipo_evaluacion: String[50]
  +activo: Boolean
}

' ══════════════════════════════════════════
' ACTORES
' ══════════════════════════════════════════

class Actor <<entity>> {
  +id: Integer {PK}
  +nombre: String[300]
  +tipo: TipoActor
  +descripcion: Text
  +direccion: String[300]
  +municipio: String[100]
  +estado: String[100]
  +pais: String[100]
  +telefono: String[20]
  +correo: String[100]
  +sitio_web: String[200]
  +redes_sociales: JSON
  +activo: Boolean
}

enum TipoActor <<enumeration>> {
  gobierno
  civil
  empresa
  persona_fisica
}

class ResponsableActor <<entity>> {
  +id: Integer {PK}
  +actor_id: Integer {FK → actores}
  +nombre: String[200]
  +cargo: String[150]
  +telefono: String[20]
  +correo: String[100]
  +es_principal: Boolean
}

class HorarioActor <<entity>> {
  +id: Integer {PK}
  +actor_id: Integer {FK → actores}
  +dia_semana: String[20]
  +hora_inicio: String[10]
  +hora_fin: String[10]
  +activo: Boolean
}

class ServicioActor <<entity>> {
  +id: Integer {PK}
  +actor_id: Integer {FK → actores}
  +derecho_id: Integer {FK → derechos}
  +nombre: String[300]
  +descripcion: Text
  +tipo: TipoServicio
  +es_gratuito: Boolean
  +costo: Decimal
  +disponibilidad: String[100]
  +duracion_estimada: String[100]
  +activo: Boolean
}

enum TipoServicio <<enumeration>> {
  servicio
  producto
}

class RequisitoServicio <<entity>> {
  +id: Integer {PK}
  +servicio_id: Integer {FK → actores_servicios}
  +descripcion: String[500]
  +procedimiento_acceso: Text
  +documentacion_requerida: Text
}

' ══════════════════════════════════════════
' DIAGNÓSTICO
' ══════════════════════════════════════════

class Diagnostico <<entity>> {
  +id: Integer {PK}
  +caso_nna_id: Integer {FK → nna_casos}
  +tipo: TipoDiagnostico
  +fecha: Date
  +responsable_id: Integer {FK → users}
  +observaciones: Text
  +completado: Boolean
  +fecha_creacion: DateTime
}

enum TipoDiagnostico <<enumeration>> {
  inicial
  nna
  tutor
  entorno
}

class IndicadorDiagnostico <<entity>> {
  +id: Integer {PK}
  +diagnostico_id: Integer {FK → diagnosticos}
  +indicador_id: Integer {FK → indicadores}
  +valor: String[20]
  +observacion: Text
  +vulnerado: Boolean
}

class DerechoVulnerado <<entity>> {
  +id: Integer {PK}
  +diagnostico_id: Integer {FK → diagnosticos}
  +derecho_id: Integer {FK → derechos}
  +severidad: SeveridadVulneracion
  +recomendacion: Text
  +generado_automaticamente: Boolean
}

enum SeveridadVulneracion <<enumeration>> {
  leve
  moderada
  grave
  critica
}

' ══════════════════════════════════════════
' PLAN DE RESTITUCIÓN
' ══════════════════════════════════════════

class PlanRestitucion <<entity>> {
  +id: Integer {PK}
  +caso_nna_id: Integer {FK → nna_casos}
  +objetivo: Text
  +derechos_afectados: JSON
  +responsable_id: Integer {FK → users}
  +fecha_inicio: Date
  +fecha_termino: Date
  +estado: EstadoPlan
  +observaciones: Text
  +fecha_creacion: DateTime
}

enum EstadoPlan <<enumeration>> {
  borrador
  activo
  pausado
  completado
  cancelado
}

class MedidaRestitucion <<entity>> {
  +id: Integer {PK}
  +plan_id: Integer {FK → planes_restitucion}
  +tipo: TipoMedida
  +descripcion: Text
  +responsable_id: Integer {FK → users}
  +actor_id: Integer {FK → actores}
  +recursos_requeridos: Text
  +estado: EstadoMedida
  +porcentaje_avance: Integer
  +fecha_inicio: Date
  +fecha_limite: Date
  --
  +calcular_avance(): Integer
  +esta_vencida(): Boolean
}

enum TipoMedida <<enumeration>> {
  psicologica
  legal
  medica
  educativa
  social
  economica
  otra
}

enum EstadoMedida <<enumeration>> {
  pendiente
  en_proceso
  completada
  cancelada
}

class SeguimientoMedida <<entity>> {
  +id: Integer {PK}
  +medida_id: Integer {FK → medidas_restitucion}
  +registrado_por_id: Integer {FK → users}
  +fecha_seguimiento: Date
  +descripcion_avance: Text
  +porcentaje_cumplimiento: Integer
  +observaciones: Text
  +evidencias: JSON
  +fecha_creacion: DateTime
}

' ══════════════════════════════════════════
' AUDITORÍA
' ══════════════════════════════════════════

class AuditLog <<entity>> {
  +id: Integer {PK}
  +usuario_id: Integer {FK → users}
  +accion: String[100]
  +entidad: String[100]
  +entidad_id: Integer
  +detalles: JSON
  +fecha: DateTime
}

' ══════════════════════════════════════════
' RELACIONES
' ══════════════════════════════════════════

User "1" --> "0..*" CasoNNA          : crea >
User "1" --> "0..*" Diagnostico      : es responsable de >
User "1" --> "0..*" PlanRestitucion  : es responsable de >
User "1" --> "0..*" MedidaRestitucion: es responsable de >
User "1" --> "0..*" SeguimientoMedida: registra >
User "1" --> "0..*" AuditLog         : genera >

CasoNNA "1" *-- "0..1" TutorNNA         : tiene ◆
CasoNNA "1" *-- "0..1" DatosMedicosNNA  : tiene ◆
CasoNNA "1" *-- "0..*" PersonaFamiliar  : tiene ◆
CasoNNA "1" *-- "0..*" RelacionFamiliar : tiene ◆
CasoNNA "1" *-- "0..1" Familiograma     : tiene ◆
CasoNNA "1" *-- "0..*" Diagnostico      : tiene ◆
CasoNNA "1" *-- "0..*" PlanRestitucion  : tiene ◆

CasoNNA --> GeneroNNA       : genero
CasoNNA --> EstadoCasoNNA   : estado
PersonaFamiliar --> TipoSimboloFamiliar : tipo_simbolo
RelacionFamiliar --> TipoRelacionFamiliar : tipo_relacion

Derecho --> CategoriaDerecho    : categoria
Derecho "1" *-- "0..*" Indicador : tiene ◆
Derecho "1" o-- "0..*" ServicioActor : atiende

Actor --> TipoActor           : tipo
Actor "1" *-- "0..*" ResponsableActor : tiene ◆
Actor "1" *-- "0..*" HorarioActor     : tiene ◆
Actor "1" *-- "0..*" ServicioActor    : ofrece ◆
ServicioActor "1" *-- "0..*" RequisitoServicio : requiere ◆
ServicioActor --> TipoServicio : tipo

Diagnostico --> TipoDiagnostico : tipo
Diagnostico "1" *-- "0..*" IndicadorDiagnostico : evalua ◆
Diagnostico "1" *-- "0..*" DerechoVulnerado      : genera ◆
IndicadorDiagnostico --> Indicador  : evalua
DerechoVulnerado --> Derecho        : vulnerado
DerechoVulnerado --> SeveridadVulneracion : severidad

PlanRestitucion --> EstadoPlan : estado
PlanRestitucion "1" *-- "0..*" MedidaRestitucion : contiene ◆
MedidaRestitucion "1" *-- "0..*" SeguimientoMedida : registra ◆
MedidaRestitucion --> TipoMedida : tipo
MedidaRestitucion --> EstadoMedida : estado
MedidaRestitucion "0..*" --> "0..1" Actor : apoya

@enduml
```

### 3.5.2 Clases Boundary (Interfaz con el Usuario)

Las clases Boundary representan los puntos de contacto entre los actores externos y el sistema:

```
@startuml Xolix_ClasesBoundary

skinparam classBackgroundColor #E8F8F5
skinparam classBorderColor #1ABC9C

title Clases Boundary — Xolix 3.0

class IULogin <<boundary>> {
  -formulario_login: Form
  --
  +renderFormulario(): void
  +capturarCredenciales(): {correo, password}
  +mostrarError(mensaje: String): void
  +redirigirDashboard(): void
}

class IUExpediente <<boundary>> {
  -formulario_caso: Form
  -lista_casos: Table
  --
  +renderFormularioCreacion(): void
  +renderListaCasos(casos: List): void
  +renderDetalleCaso(caso: CasoNNAResponse): void
  +capturarDatosNNA(): CasoNNACreate
  +capturarDatosTutor(): TutorCreate
  +capturarDatosMedicos(): DatosMedicosCreate
  +mostrarError(campo: String, msg: String): void
}

class IUFamiliograma <<boundary>> {
  -canvas_reactflow: ReactFlowCanvas
  -panel_personas: Panel
  -panel_relaciones: Panel
  --
  +renderCanvas(grafo: JSON): void
  +agregarNodo(persona: PersonaFamiliar): void
  +agregarArista(relacion: RelacionFamiliar): void
  +exportarImagen(): Blob
  +capturarEstadoGrafo(): JSON
}

class IUDiagnostico <<boundary>> {
  -selector_tipo: Select
  -lista_indicadores: CheckboxList
  -campo_observaciones: TextArea
  --
  +renderTiposDiagnostico(): void
  +renderIndicadoresPorDerecho(indicadores: List): void
  +capturarEvaluacion(): DiagnosticoCreate
  +mostrarDerechosVulnerados(derechos: List): void
  +renderHistorial(diagnosticos: List): void
}

class IUPlan <<boundary>> {
  -formulario_plan: Form
  -lista_medidas: List
  -panel_seguimiento: Panel
  --
  +renderFormularioPlan(): void
  +renderMedidas(medidas: List): void
  +renderSeguimientos(seguimientos: List): void
  +capturarPlan(): PlanCreate
  +capturarSeguimiento(medida_id: Integer): SeguimientoCreate
  +mostrarBarraAvance(porcentaje: Integer): void
}

class IUActor <<boundary>> {
  -formulario_actor: Form
  -filtros_busqueda: FilterPanel
  -lista_actores: Table
  --
  +renderListaActores(actores: List): void
  +renderDetalleActor(actor: ActorResponse): void
  +renderFiltros(): void
  +capturarFiltros(): {municipio, tipo, derecho_id}
  +capturarActor(): ActorCreate
}

class IUReportes <<boundary>> {
  -panel_kpi: Dashboard
  -grafica_derechos: BarChart
  -grafica_evolucion: LineChart
  --
  +renderKPIs(indicadores: Dict): void
  +renderGraficaDerechos(datos: List): void
  +renderGraficaEvolucion(datos: List): void
  +solicitarExportacionPDF(): void
  +solicitarExportacionExcel(): void
}

@enduml
```

### 3.5.3 Clases Control (Lógica del Caso de Uso)

```
@startuml Xolix_ClasesControl

skinparam classBackgroundColor #FEF9E7
skinparam classBorderColor #F39C12

title Clases Control — Xolix 3.0

class AccessCtr <<control>> {
  --
  +autenticar(correo: String, password: String, db: Session): TokenResponse
  +verificar_token(token: String): UserPayload
  +obtener_usuario_actual(token: String, db: Session): User
  +verificar_rol(usuario: User, roles: List[String]): bool
}

class ExpedienteCtr <<control>> {
  --
  +crear_caso(datos: CasoNNACreate, creador_id: int, db: Session): CasoNNA
  +obtener_caso(caso_id: int, db: Session): CasoNNA
  +listar_casos(filtros: dict, db: Session): List[CasoNNA]
  +actualizar_caso(caso_id: int, datos: CasoNNAUpdate, db: Session): CasoNNA
  +upsert_tutor(caso_id: int, datos: TutorCreate, db: Session): TutorNNA
  +upsert_datos_medicos(caso_id: int, datos: DatosMedicosCreate, db: Session): DatosMedicosNNA
}

class FamiliogramaCtr <<control>> {
  --
  +agregar_persona(caso_id: int, datos: PersonaCreate, db: Session): PersonaFamiliar
  +listar_personas(caso_id: int, db: Session): List[PersonaFamiliar]
  +agregar_relacion(caso_id: int, datos: RelacionCreate, db: Session): RelacionFamiliar
  +guardar_familiograma(caso_id: int, grafo_json: dict, db: Session): Familiograma
  +obtener_familiograma(caso_id: int, db: Session): Familiograma
}

class DiagnosticoCtr <<control>> {
  --
  +crear_diagnostico(datos: DiagnosticoCreate, responsable_id: int, db: Session): Diagnostico
  +evaluar_indicadores(diag_id: int, evaluaciones: List, db: Session): List[IndicadorDiagnostico]
  +generar_derechos_vulnerados(diag_id: int, db: Session): List[DerechoVulnerado]
  +listar_diagnosticos(caso_id: int, db: Session): List[Diagnostico]
  +resumen_derechos_vulnerados(caso_id: int, db: Session): dict
}

class ActorCtr <<control>> {
  --
  +crear_actor(datos: ActorCreate, db: Session): Actor
  +buscar_actores(municipio: str, derecho_id: int, tipo: str, db: Session): List[Actor]
  +obtener_actor(actor_id: int, db: Session): Actor
  +agregar_servicio(actor_id: int, datos: ServicioCreate, db: Session): ServicioActor
  +listar_actores(filtros: dict, db: Session): List[Actor]
}

class PlanCtr <<control>> {
  --
  +crear_plan(datos: PlanCreate, responsable_id: int, db: Session): PlanRestitucion
  +agregar_medida(plan_id: int, datos: MedidaCreate, db: Session): MedidaRestitucion
  +registrar_seguimiento(medida_id: int, datos: SeguimientoCreate, registrador_id: int, db: Session): SeguimientoMedida
  +actualizar_avance_medida(medida_id: int, porcentaje: int, db: Session): MedidaRestitucion
  +listar_planes(caso_id: int, db: Session): List[PlanRestitucion]
}

class ReporteCtr <<control>> {
  --
  +calcular_indicadores_globales(db: Session): dict
  +frecuencia_derechos_vulnerados(db: Session): List[dict]
  +evolucion_casos(meses: int, db: Session): List[dict]
  +generar_pdf_casos(db: Session): StreamingResponse
  +generar_excel_casos(db: Session): StreamingResponse
  +generar_excel_actores(db: Session): StreamingResponse
}

class AuditCtr <<control>> {
  --
  +registrar(usuario_id: int, accion: str, entidad: str, entidad_id: int, detalles: dict, db: Session): AuditLog
  +listar_auditoria(db: Session, filtros: dict): List[AuditLog]
}

@enduml
```
