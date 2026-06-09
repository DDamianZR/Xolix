---
title: "XOLIX 3.0 — Documento de Diseño del Sistema"
subtitle: "Plataforma de Gestión Integral de NNA para Fundación de Restitución de Derechos"
version: "3.0"
fecha: "Junio 2026"
institución: "Escuela Superior de Cómputo — Instituto Politécnico Nacional"
materia: "Análisis y Diseño de Sistemas"
---

# XOLIX 3.0
## Documento de Diseño del Sistema

**Proyecto:** Plataforma web para la gestión integral de Niñas, Niños y Adolescentes (NNA) atendidos por una fundación dedicada a la restitución de derechos.

**Versión:** 3.0  
**Fecha:** Junio 2026  
**Institución:** Escuela Superior de Cómputo — Instituto Politécnico Nacional  
**Materia:** Análisis y Diseño de Sistemas

---

## Equipo de Desarrollo

| Rol | Nombre |
|---|---|
| Arquitecto de Software | DDamianZR |
| Analista de Sistemas | — |
| Diseñador UML | — |
| Desarrollador Backend | — |
| Desarrollador Frontend | — |

---

## Historial de Revisiones

| Versión | Fecha | Descripción |
|---|---|---|
| 1.0 | Feb 2026 | Diseño inicial: autenticación, usuarios, expedientes |
| 2.0 | Mar 2026 | Agregado familiograma interactivo y entrevistas |
| 3.0 | Jun 2026 | Módulos completos: actores, diagnósticos, planes, auditoría, reportes |

---

## Tabla de Contenido

1. [Organización del Diseño](secciones/01_organizacion_diseno.md)
   - 1.1 Lineamientos de Diseño (SOLID, DRY, KISS, Clean Architecture)
   - 1.2 Metodología
   - 1.3 Notación UML
   - 1.4 Alcance del Diseño

2. [Diseño Arquitectónico](secciones/02_arquitectura.md)
   - 2.1 Objetivos de la Arquitectura
   - 2.2 Diagrama Arquitectónico (Componentes + Despliegue)
   - 2.3 Explicación de Capas
   - 2.4 Beneficios y Limitaciones

3. [Diseño Estático](secciones/03_diseno_estatico.md)
   - 3.1 Descripción General
   - 3.2 Diseño de Subsistemas (Seguridad, Expedientes, Diagnósticos, Planeación, Actores, Familiograma)
   - 3.3 Diseño de Módulos
   - 3.4 Diseño de Paquetes
   - 3.5 Diseño de Clases (BCE: Boundary, Control, Entity)

4. [Diseño Dinámico](secciones/04_diseno_dinamico.md)
   - 4.1 Login
   - 4.2 Crear Expediente
   - 4.3 Editar Expediente
   - 4.4 Registrar Diagnóstico
   - 4.5 Determinar Derechos Vulnerados
   - 4.6 Buscar Actores
   - 4.7 Crear Plan de Restitución
   - 4.8 Registrar Seguimiento
   - 4.9 Generar Familiograma

5. [Diseño de Persistencia](secciones/05_persistencia.md)
   - 5.1 Modelo Relacional Completo
   - 5.2 Diccionario de Datos (15 tablas principales)
   - 5.3 Catálogo de Consultas (12 queries documentados)
   - 5.4 Índices y Restricciones

---

## Resumen Ejecutivo

Xolix 3.0 es una plataforma web desarrollada para apoyar a una fundación dedicada a la atención y restitución de derechos de Niñas, Niños y Adolescentes (NNA) en situación de vulnerabilidad.

El sistema implementa una arquitectura en cinco capas: presentación (React 18 + Vite), controladores REST (FastAPI), servicios de negocio (Python 3.12), repositorio ORM (SQLAlchemy 2.0) y persistencia (PostgreSQL 18). La comunicación entre el frontend y el backend se realiza mediante una API REST documentada con OpenAPI/Swagger y protegida con JWT.

El diseño sigue los principios SOLID, el patrón Boundary-Control-Entity (BCE) y la arquitectura limpia (Clean Architecture), garantizando alta cohesión, bajo acoplamiento, seguridad por diseño y escalabilidad modular.

### Módulos Implementados

| Módulo | Descripción | Estado |
|---|---|---|
| Autenticación (JWT + RBAC) | Login con roles: director, coordinador, psicólogo, trabajador social, legal | ✅ Completo |
| Gestión de Usuarios | CRUD de personal con validación de RFC/CURP | ✅ Completo |
| Expedientes NNA | Caso, tutor, datos médicos, cartilla de vacunación | ✅ Completo |
| Familiograma Interactivo | Canvas ReactFlow, personas, relaciones familiares | ✅ Completo |
| Actores en Materia de Derechos | Directorio con servicios, horarios, filtros por municipio/derecho | ✅ Completo |
| Diagnósticos | 4 tipos, evaluación de indicadores, derechos vulnerados automáticos | ✅ Completo |
| Planes de Restitución | Planes, medidas por tipo, seguimientos con avance | ✅ Completo |
| Auditoría | Registro automático de todas las operaciones críticas | ✅ Completo |
| Exportación | PDF y Excel de casos, actores y diagnósticos | ✅ Completo |
| Reportes e Indicadores | KPIs globales, frecuencia de derechos vulnerados, evolución mensual | ✅ Completo |

### Estadísticas del Sistema

| Indicador | Valor |
|---|---|
| Tablas en base de datos | 37 |
| Endpoints de API REST | 65+ |
| Casos de uso documentados | 9 |
| Diagramas de secuencia UML | 9 |
| Clases del dominio | 16 |
| Clases BCE total | 30+ |
| Consultas SQL documentadas | 12 |
| Módulos de negocio | 8 |

---

## Instrucciones para Usar los Diagramas UML

Los diagramas de este documento están escritos en sintaxis PlantUML. Para visualizarlos:

### Opción 1: Visual Paradigm / StarUML / Enterprise Architect
1. Abrir la herramienta CASE
2. Crear un nuevo diagrama del tipo correspondiente
3. En el editor de código PlantUML, pegar el contenido del bloque `@startuml...@enduml`
4. La herramienta generará el diagrama automáticamente

### Opción 2: PlantUML Online
1. Acceder a https://www.plantuml.com/plantuml/uml/
2. Pegar el contenido del bloque entre `@startuml` y `@enduml`
3. El diagrama se genera en tiempo real

### Opción 3: VS Code con extensión PlantUML
1. Instalar la extensión "PlantUML" de jebbs
2. Abrir el archivo `.puml` o el bloque de código
3. Presionar `Alt+D` para previsualizar

### Opción 4: IntelliJ IDEA / WebStorm
1. Instalar el plugin "PlantUML integration"
2. Pegar el código en un archivo `.puml`
3. El diagrama se genera en el panel lateral

---

*Documento generado para el proyecto académico Xolix 3.0 — Análisis y Diseño de Sistemas — IPN ESCOM — 2026*
