# 1. ORGANIZACIÓN DEL DISEÑO

---

## 1.1 Lineamientos de Diseño

El diseño de Xolix 3.0 se rige por un conjunto de principios de ingeniería de software que garantizan la calidad, mantenibilidad y evolución del sistema a lo largo del tiempo. A continuación se detalla cada principio y su aplicación concreta en el sistema.

### 1.1.1 Principios SOLID

Los principios SOLID constituyen la base del diseño orientado a objetos de calidad. Su aplicación en Xolix 3.0 se describe a continuación:

**S — Single Responsibility Principle (Principio de Responsabilidad Única)**

Cada clase, módulo o componente debe tener una única razón para cambiar. En Xolix 3.0 esto se materializa de la siguiente manera:

- La clase `ExpedienteService` se ocupa exclusivamente de la lógica de negocio relacionada con el ciclo de vida del expediente (crear, actualizar, archivar). No tiene ninguna responsabilidad de presentación ni de persistencia directa.
- Los routers de FastAPI (`expedientes.py`, `diagnosticos.py`, `planes.py`) actúan únicamente como puntos de entrada HTTP; delegan toda la lógica a la capa de servicios.
- Los modelos SQLAlchemy (`CasoNNA`, `Diagnostico`, `PlanRestitucion`) son responsables exclusivamente del mapeo objeto-relacional.

**O — Open/Closed Principle (Principio Abierto/Cerrado)**

Las entidades de software deben estar abiertas para extensión y cerradas para modificación. En Xolix 3.0:

- El sistema de roles (`director`, `coordinador`, `psicologo`, `trabajador_social`, `legal`) se implementa mediante el decorador `require_role(*roles)` en `dependencies.py`. Para agregar un nuevo rol no es necesario modificar ningún router existente; basta con actualizar la lista de roles permitidos en la llamada al decorador.
- Las categorías de derechos se modelan como enumeraciones extensibles (`CategoriaDerecho`). Agregar una nueva categoría no modifica la lógica de validación existente.

**L — Liskov Substitution Principle (Principio de Sustitución de Liskov)**

Los objetos de una subclase deben poder usarse en lugar de objetos de su superclase sin alterar el comportamiento del programa. En Xolix 3.0:

- Los esquemas Pydantic de respuesta (`CasoNNAResponse`) extienden los esquemas base manteniendo compatibilidad total de tipos. Un endpoint que recibe `CasoNNACreate` puede ser reemplazado por `CasoNNAUpdate` sin romper el contrato de la API.
- Las enumeraciones de estado (`EstadoCasoNNA`, `EstadoPlan`) son subtipos de `str` en Python, lo que permite que sean tratadas como cadenas de texto ordinarias en cualquier contexto que espere un `str`.

**I — Interface Segregation Principle (Principio de Segregación de Interfaces)**

Los clientes no deben verse forzados a depender de interfaces que no utilizan. En Xolix 3.0:

- Los schemas Pydantic están separados por operación: `CasoNNACreate`, `CasoNNAUpdate` y `CasoNNAResponse` son clases distintas. Un servicio que solo lee expedientes importa únicamente `CasoNNAResponse`, sin verse afectado por los campos requeridos en creación.
- Los routers están organizados por dominio de negocio, no por tipo de operación. Esto evita que un módulo cliente (por ejemplo, el de diagnósticos) dependa de las operaciones de planes.

**D — Dependency Inversion Principle (Principio de Inversión de Dependencias)**

Los módulos de alto nivel no deben depender de módulos de bajo nivel; ambos deben depender de abstracciones. En Xolix 3.0:

- Los servicios reciben la sesión de base de datos mediante inyección de dependencias de FastAPI (`db: Session = Depends(get_db)`). El servicio no instancia ni gestiona directamente la conexión a PostgreSQL.
- Las dependencias de autenticación (`get_current_user`) y autorización (`require_role`) se inyectan en los endpoints, no se invocan directamente. Esto permite sustituirlas en pruebas sin modificar la lógica de negocio.

### 1.1.2 DRY — Don't Repeat Yourself

El principio DRY establece que cada pieza de conocimiento debe tener una representación única, no ambigua y autoritativa dentro de un sistema.

En Xolix 3.0:

- La validación de CURP y RFC se centraliza en `validators/mexican_ids.py`. Ningún router ni servicio repite esta lógica.
- El cliente HTTP del frontend se encapsula en `src/api/client.js`, que gestiona la adición del token JWT en cada petición. Los componentes React no repiten la lógica de autenticación en cada llamada.
- La función `registrar_audit()` en `extras_service.py` centraliza el registro de auditoría. Todos los servicios que necesitan registrar acciones la llaman en lugar de escribir directamente en la tabla `audit_logs`.
- Los estilos de la interfaz se definen mediante variables CSS globales en `index.css` (`--primary`, `--neo-shadow`, `--radius-sm`). Los componentes referencias las variables, no valores hexadecimales repetidos.

### 1.1.3 KISS — Keep It Simple, Stupid

El principio KISS establece que la mayoría de los sistemas funcionan mejor si se mantienen simples en lugar de complejos.

En Xolix 3.0:

- Los endpoints REST siguen convenciones estándar de HTTP (GET para consultas, POST para creación, PUT para actualización, DELETE para eliminación). No se inventan convenciones propietarias.
- La autenticación se basa en JWT estándar (RFC 7519) sin capas adicionales de complejidad. El token contiene únicamente el `user_id` y el `rol`, que son los datos mínimos necesarios.
- El familiograma se almacena como JSON en PostgreSQL en lugar de modelar un grafo relacional complejo. Esto simplifica drásticamente las operaciones de lectura y escritura, que son las más frecuentes para el familiograma.

### 1.1.4 Clean Architecture

La arquitectura limpia (Robert C. Martin) establece que las reglas de negocio son el núcleo del sistema y no deben depender de frameworks, bases de datos o interfaces de usuario.

En Xolix 3.0 las capas son:

```
┌─────────────────────────────────────────────────┐
│  Frameworks & Drivers                           │
│  (FastAPI, React, PostgreSQL, SQLAlchemy)       │
├─────────────────────────────────────────────────┤
│  Interface Adapters                             │
│  (Routers, Schemas Pydantic, Components JSX)   │
├─────────────────────────────────────────────────┤
│  Use Cases / Application Services              │
│  (expediente_service, diagnostico_service...)  │
├─────────────────────────────────────────────────┤
│  Entities / Domain                             │
│  (CasoNNA, Diagnostico, PlanRestitucion...)    │
└─────────────────────────────────────────────────┘
```

La regla de dependencia se respeta: las entidades de dominio no importan nada de FastAPI; los servicios no importan nada de los routers; los modelos no importan nada de los schemas.

### 1.1.5 Baja Dependencia (Bajo Acoplamiento)

El acoplamiento se minimiza mediante:

- **Inyección de dependencias:** FastAPI provee `Depends()` para inyectar sesiones de BD y dependencias de seguridad sin acoplar los handlers al ciclo de vida de la aplicación.
- **Separación de modelos ORM y schemas:** los modelos SQLAlchemy nunca se serializan directamente a JSON; los schemas Pydantic actúan como capa de transformación, evitando que cambios en la BD afecten directamente la API.
- **API REST:** el frontend y el backend están desacoplados por contrato HTTP. El frontend puede desarrollarse o probarse independientemente.

### 1.1.6 Alta Cohesión

Cada módulo agrupa únicamente lo que pertenece al mismo dominio conceptual:

- El paquete `app/models/diagnostico.py` contiene `Diagnostico`, `IndicadorDiagnostico` y `DerechoVulnerado`: entidades que solo tienen sentido en el contexto del diagnóstico.
- El paquete `app/routers/planes.py` expone únicamente los endpoints relacionados con planes de restitución.
- Los componentes React `DiagnosticoPage.jsx` y `PlanesPage.jsx` son responsables exclusivamente de su dominio funcional.

### 1.1.7 Seguridad por Diseño

- **Autenticación:** JWT con expiración configurable (`ACCESS_TOKEN_EXPIRE_MINUTES`).
- **Autorización:** RBAC implementado mediante el decorador `require_role(*roles)` aplicado a nivel de endpoint.
- **Hashing de contraseñas:** bcrypt con factor de costo configurable.
- **Variables de entorno:** credenciales en `.env`, nunca en código fuente.
- **Validación de entrada:** Pydantic valida todos los datos antes de que lleguen a la capa de servicios.
- **Auditoría:** todas las operaciones críticas quedan registradas en `audit_logs` con usuario, acción, entidad e identidad de registro.

### 1.1.8 Escalabilidad

- **Horizontal:** al ser una aplicación sin estado (stateless) con JWT, múltiples instancias del backend pueden ejecutarse simultáneamente detrás de un balanceador.
- **Vertical:** SQLAlchemy gestiona un pool de conexiones configurable a PostgreSQL.
- **Modular:** cada módulo de negocio (Expedientes, Diagnósticos, Actores, Planes) puede evolucionar o migrarse independientemente.

### 1.1.9 Reutilización

- Los componentes React (`Topbar`, tarjetas de estado, formularios reutilizables) están diseñados como unidades independientes con props bien definidas.
- Los servicios de exportación (`export_service.py`) son reutilizables por cualquier módulo que necesite generar PDF o Excel.
- El catálogo de derechos e indicadores es compartido por el módulo de diagnósticos y el de planes.

---

## 1.2 Metodología

### 1.2.1 UML 2.x

El diseño utiliza la versión 2.x del Unified Modeling Language según el estándar de la Object Management Group (OMG). Los diagramas producidos son compatibles con herramientas CASE profesionales como Visual Paradigm, StarUML y Enterprise Architect.

Los tipos de diagrama utilizados en este documento son:

| Tipo de Diagrama | Estándar UML | Propósito |
|---|---|---|
| Diagrama de Componentes | UML 2.x §15 | Arquitectura del sistema |
| Diagrama de Despliegue | UML 2.x §19 | Infraestructura física/virtual |
| Diagrama de Clases | UML 2.x §9 | Estructura estática del dominio |
| Diagrama de Paquetes | UML 2.x §12 | Organización modular |
| Diagrama de Secuencia | UML 2.x §17 | Comportamiento dinámico |

### 1.2.2 Diseño Orientado a Objetos

El diseño aplica los conceptos fundamentales del paradigma orientado a objetos:

- **Abstracción:** las clases del dominio (`CasoNNA`, `Diagnostico`) modelan conceptos del mundo real de la gestión de NNA, ocultando los detalles de implementación.
- **Encapsulamiento:** los atributos de las entidades son privados; el acceso se controla mediante métodos de servicio.
- **Herencia:** los schemas Pydantic usan herencia (`CasoNNAUpdate` hereda de `CasoNNACreate`) para reutilizar validaciones.
- **Polimorfismo:** los distintos tipos de diagnóstico (`inicial`, `nna`, `tutor`, `entorno`) comparten la misma interfaz de gestión.

### 1.2.3 Casos de Uso

Los casos de uso se modelan siguiendo la notación UML estándar e identifican las interacciones entre los actores del sistema (Director, Coordinador, Psicólogo, Trabajador Social, Legal) y las funcionalidades del sistema.

Los casos de uso cubren los nueve procesos principales descritos en la Sección 4 (Diseño Dinámico).

### 1.2.4 Desarrollo Iterativo e Incremental

El proyecto se desarrolló en tres iteraciones:

| Iteración | Módulos entregados | Estado |
|---|---|---|
| 1 | Usuarios, Expedientes, Procesos | Completada |
| 2 | Familiograma (interactivo), Personas, Relaciones | Completada |
| 3 | Actores, Diagnósticos, Planes, Auditoría, Reportes | Completada |

Cada iteración produjo un incremento funcional y demostrable, siguiendo el ciclo: Análisis → Diseño → Implementación → Prueba → Integración.

---

## 1.3 Notación

### 1.3.1 Diagrama de Clases UML

| Elemento | Notación | Significado |
|---|---|---|
| `+atributo: Tipo` | Visibilidad pública | Atributo público |
| `-atributo: Tipo` | Visibilidad privada | Atributo privado |
| `#atributo: Tipo` | Visibilidad protegida | Atributo protegido |
| `──────>` | Asociación | Relación estructural |
| `◆──────` | Composición | El todo controla el ciclo de vida |
| `◇──────` | Agregación | Asociación "parte de" débil |
| `──────▷` | Herencia/Generalización | Subclase → Superclase |
| `- - - ->` | Dependencia | Uso transitorio |
| `1`, `0..1`, `*`, `1..*` | Multiplicidad | Cardinalidad de la relación |

### 1.3.2 Diagrama de Secuencia UML

| Elemento | Notación | Significado |
|---|---|---|
| `:Actor` | Figura de palo + lifeline | Agente externo |
| `:IUxxx` | Rectángulo + lifeline | Clase Boundary |
| `:xxxCtr` | Círculo con flecha + lifeline | Clase Control |
| `:ORMxxx` | Elipse + lifeline | Clase Entity |
| `:PostgreSQL` | Cilindro + lifeline | Base de datos |
| `──────>` | Mensaje síncrono | Llamada bloqueante |
| `──────>>` | Mensaje asíncrono | Llamada no bloqueante |
| `<──────` | Retorno | Valor de retorno |
| `▌` | Barra de activación | Objeto en ejecución |
| `loop[cond]` | Fragmento combinado | Iteración |
| `alt[cond]` | Fragmento combinado | Alternativa (if/else) |
| `opt[cond]` | Fragmento combinado | Opcional (if sin else) |
| `ref` | Fragmento de referencia | Referencia a otro diagrama |

### 1.3.3 Patrón BCE (Boundary-Control-Entity)

El patrón BCE organiza las clases de un caso de uso en tres categorías:

| Categoría | Estereotipo | Responsabilidad |
|---|---|---|
| **Boundary** | `<<boundary>>` | Interfaz con actores externos (UI, API). Traduce entre el mundo externo y el sistema. |
| **Control** | `<<control>>` | Orquesta la lógica del caso de uso. Coordina Boundaries y Entities. |
| **Entity** | `<<entity>>` | Representa objetos de dominio persistibles. Encapsula datos y reglas de negocio. |

En la implementación Xolix 3.0, el mapeo es:

```
Boundary  ←→  Router FastAPI / Componente React
Control   ←→  Service (expediente_service.py, diagnostico_service.py...)
Entity    ←→  Modelo SQLAlchemy (CasoNNA, Diagnostico, Actor...)
```

### 1.3.4 Diagrama de Paquetes UML

Los paquetes se representan con la notación de pestaña UML. Las dependencias entre paquetes se muestran con flechas punteadas (`- - →`). Un paquete que importa a otro tiene una dependencia hacia él.

### 1.3.5 Modelo Relacional

El modelo relacional se representa con notación crow's foot (pata de gallo):

| Símbolo | Significado |
|---|---|
| `‖──` | Uno (obligatorio) |
| `o──` | Cero o uno (opcional) |
| `>──` | Muchos |
| `>o──` | Cero o muchos |

---

## 1.4 Alcance del Diseño

### 1.4.1 Lo que cubre este documento

El presente Documento de Diseño cubre los siguientes aspectos del sistema Xolix 3.0:

1. **Diseño arquitectónico:** estructura en capas, componentes y sus responsabilidades.
2. **Diseño estático:** estructura de clases, subsistemas, módulos, paquetes y sus interrelaciones.
3. **Diseño dinámico:** comportamiento del sistema en los nueve casos de uso principales mediante diagramas de secuencia.
4. **Diseño de persistencia:** modelo relacional completo, diccionario de datos y catálogo de consultas SQL.
5. **Aplicación del patrón BCE** en todos los diagramas dinámicos.
6. **Decisiones de diseño justificadas:** cada decisión significativa se acompaña de una justificación técnica.

### 1.4.2 Lo que NO cubre este documento

- **Diseño de pruebas:** las estrategias de pruebas unitarias, de integración y de aceptación se documentan en el Plan de Pruebas (documento independiente).
- **Diseño de infraestructura de producción:** balanceadores de carga, contenedores Docker, pipelines CI/CD y configuración de servidores en producción se describen en el documento de despliegue.
- **Interfaz móvil:** Xolix 3.0 es exclusivamente una aplicación web responsiva. No existe versión móvil nativa en el alcance actual.
- **Módulo de Business Intelligence:** los reportes actuales son operacionales. Los dashboards analíticos avanzados (OLAP, predicciones) quedan fuera del alcance.
- **Integración con sistemas externos:** en este momento el sistema no se integra con sistemas de registro civil, IMSS, DIF ni otras plataformas gubernamentales.

### 1.4.3 Versión del sistema cubierta

Este documento corresponde a la versión **3.0** de Xolix, que incluye los módulos:

- Gestión de Usuarios y Autenticación (v1.0)
- Expedientes Digitales (v1.0)
- Procesos/Tareas (v1.0)
- Familiograma Interactivo (v2.0)
- Actores en Materia de Derechos (v3.0)
- Diagnósticos y Derechos Vulnerados (v3.0)
- Planes de Restitución y Seguimientos (v3.0)
- Auditoría y Exportación (v3.0)
- Reportes e Indicadores Globales (v3.0)
