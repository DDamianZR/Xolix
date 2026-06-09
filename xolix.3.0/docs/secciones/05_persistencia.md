# 5. DISEÑO DE PERSISTENCIA

---

## 5.1 Modelo Relacional

### 5.1.1 Diagrama Entidad-Relación

```
@startuml Xolix_ModeloRelacional

skinparam linetype ortho
skinparam backgroundColor #FAFAFA

title Modelo Relacional — Xolix 3.0\nNotación crow's foot

' ══════════════════════════════════
' SEGURIDAD
' ══════════════════════════════════

entity "users" as U {
  *id : INTEGER <<PK>>
  --
  *nombre : VARCHAR(50)
  *apellido_paterno : VARCHAR(50)
  *apellido_materno : VARCHAR(50)
  *rfc : VARCHAR(13) <<UNIQUE>>
  *curp : VARCHAR(18) <<UNIQUE>>
  *sexo : VARCHAR(10)
  *fecha_nacimiento : DATE
  *edad : INTEGER
  *estado : VARCHAR(50)
  *municipio : VARCHAR(100)
  *colonia : VARCHAR(100)
  *calle : VARCHAR(100)
  *numero : VARCHAR(20)
  *codigo_postal : VARCHAR(5)
  calles_aledanas : TEXT
  *tipo_personal : VARCHAR(20)
  *rol : VARCHAR(30)
  *correo : VARCHAR(100) <<UNIQUE>>
  *password : VARCHAR(255)
  activo : BOOLEAN = true
  verificado : BOOLEAN = false
  foto_perfil : VARCHAR(500)
  fecha_creacion : TIMESTAMP = NOW()
}

entity "audit_logs" as AL {
  *id : INTEGER <<PK>>
  --
  usuario_id : INTEGER <<FK→users>>
  *accion : VARCHAR(100)
  entidad : VARCHAR(100)
  entidad_id : INTEGER
  detalles : JSON
  fecha : TIMESTAMP = NOW()
}

' ══════════════════════════════════
' EXPEDIENTE NNA
' ══════════════════════════════════

entity "nna_casos" as NC {
  *id : INTEGER <<PK>>
  --
  *nna_nombre : VARCHAR(200)
  nna_curp : VARCHAR(18)
  nna_fecha_nacimiento : DATE
  nna_edad : INTEGER
  nna_genero : ENUM(generonna)
  nna_nacionalidad : VARCHAR(100)
  nna_estado_civil : VARCHAR(50)
  *estado : ENUM(estadocasonna)
  *creador_id : INTEGER <<FK→users>>
  fecha_creacion : TIMESTAMP = NOW()
  fecha_actualizacion : TIMESTAMP = NOW()
}

entity "nna_tutores" as NT {
  *id : INTEGER <<PK>>
  --
  *caso_id : INTEGER <<FK→nna_casos>>
  *nombre : VARCHAR(100)
  apellido_paterno : VARCHAR(100)
  apellido_materno : VARCHAR(100)
  curp : VARCHAR(18)
  rfc : VARCHAR(13)
  *parentesco : VARCHAR(50)
  telefono : VARCHAR(20)
  correo : VARCHAR(100)
  direccion : VARCHAR(300)
  ocupacion : VARCHAR(150)
  documento_identificacion : VARCHAR(50)
  numero_documento : VARCHAR(100)
}

entity "nna_datos_medicos" as NDM {
  *id : INTEGER <<PK>>
  --
  *caso_id : INTEGER <<FK→nna_casos>>
  historial_medico : TEXT
  alergias : TEXT
  discapacidades : TEXT
  tipo_sangre : VARCHAR(5)
  medico_responsable : VARCHAR(200)
  institucion_medica : VARCHAR(200)
  cartilla_vacunacion : JSON
}

entity "nna_personas" as NP {
  *id : INTEGER <<PK>>
  --
  *caso_id : INTEGER <<FK→nna_casos>>
  *nombre : VARCHAR(200)
  edad : INTEGER
  genero : ENUM(generonna)
  rol_en_familia : VARCHAR(100)
  tipo_simbolo : ENUM(tiposimbolofamiliar)
  observaciones : TEXT
  telefono : VARCHAR(20)
  direccion : VARCHAR(300)
  ocupacion : VARCHAR(150)
  escolaridad : VARCHAR(100)
  estado_salud : VARCHAR(200)
  vive_con_nna : BOOLEAN = false
  es_responsable_legal : BOOLEAN = false
  fecha_creacion : TIMESTAMP = NOW()
}

entity "nna_relaciones_familiares" as NRF {
  *id : INTEGER <<PK>>
  --
  *caso_id : INTEGER <<FK→nna_casos>>
  *persona_origen_id : INTEGER <<FK→nna_personas>>
  *persona_destino_id : INTEGER <<FK→nna_personas>>
  *tipo_relacion : ENUM(tiporelacionfamiliar)
  descripcion : VARCHAR(300)
  bidireccional : BOOLEAN = true
}

entity "nna_familiogramas" as NF {
  *id : INTEGER <<PK>>
  --
  *caso_id : INTEGER <<FK→nna_casos>>
  grafo_json : JSON
  version : INTEGER = 1
  fecha_creacion : TIMESTAMP = NOW()
  fecha_actualizacion : TIMESTAMP = NOW()
}

entity "nna_entrevistas" as NE {
  *id : INTEGER <<PK>>
  --
  *caso_id : INTEGER <<FK→nna_casos>>
  grado_negacion : INTEGER
  completada : BOOLEAN = false
  observaciones_negacion : TEXT
  frases_comunicadas : JSON
  dia_comun : JSON
}

entity "nna_observaciones" as NO {
  *id : INTEGER <<PK>>
  --
  *caso_id : INTEGER <<FK→nna_casos>>
  persona_familiar_id : INTEGER <<FK→nna_personas>>
  tipo : VARCHAR(50)
  descripcion : TEXT
  fecha_observacion : DATE
}

' ══════════════════════════════════
' CATÁLOGO
' ══════════════════════════════════

entity "derechos" as D {
  *id : INTEGER <<PK>>
  --
  *nombre : VARCHAR(200)
  descripcion : TEXT
  categoria : ENUM(categoriaderecho)
  articulo_referencia : VARCHAR(100)
  activo : BOOLEAN = true
}

entity "indicadores" as IND {
  *id : INTEGER <<PK>>
  --
  *derecho_id : INTEGER <<FK→derechos>>
  *nombre : VARCHAR(300)
  descripcion : TEXT
  tipo_evaluacion : VARCHAR(50)
  activo : BOOLEAN = true
}

' ══════════════════════════════════
' ACTORES
' ══════════════════════════════════

entity "actores" as A {
  *id : INTEGER <<PK>>
  --
  *nombre : VARCHAR(300)
  *tipo : ENUM(tipoactor)
  descripcion : TEXT
  direccion : VARCHAR(300)
  municipio : VARCHAR(100)
  estado : VARCHAR(100)
  pais : VARCHAR(100)
  telefono : VARCHAR(20)
  correo : VARCHAR(100)
  sitio_web : VARCHAR(200)
  redes_sociales : JSON
  activo : BOOLEAN = true
}

entity "actores_responsables" as AR {
  *id : INTEGER <<PK>>
  --
  *actor_id : INTEGER <<FK→actores>>
  *nombre : VARCHAR(200)
  cargo : VARCHAR(150)
  telefono : VARCHAR(20)
  correo : VARCHAR(100)
  es_principal : BOOLEAN = false
}

entity "actores_horarios" as AH {
  *id : INTEGER <<PK>>
  --
  *actor_id : INTEGER <<FK→actores>>
  *dia_semana : VARCHAR(20)
  hora_inicio : VARCHAR(10)
  hora_fin : VARCHAR(10)
  activo : BOOLEAN = true
}

entity "actores_servicios" as AS2 {
  *id : INTEGER <<PK>>
  --
  *actor_id : INTEGER <<FK→actores>>
  derecho_id : INTEGER <<FK→derechos>>
  *nombre : VARCHAR(300)
  descripcion : TEXT
  tipo : ENUM(tiposervicio)
  es_gratuito : BOOLEAN = true
  costo : DECIMAL(10,2)
  disponibilidad : VARCHAR(100)
  duracion_estimada : VARCHAR(100)
  activo : BOOLEAN = true
}

entity "servicios_requisitos" as SR {
  *id : INTEGER <<PK>>
  --
  *servicio_id : INTEGER <<FK→actores_servicios>>
  *descripcion : VARCHAR(500)
  procedimiento_acceso : TEXT
  documentacion_requerida : TEXT
}

' ══════════════════════════════════
' DIAGNÓSTICO
' ══════════════════════════════════

entity "diagnosticos" as DG {
  *id : INTEGER <<PK>>
  --
  *caso_nna_id : INTEGER <<FK→nna_casos>>
  *tipo : ENUM(tipodiagnostico)
  *fecha : DATE
  responsable_id : INTEGER <<FK→users>>
  observaciones : TEXT
  completado : BOOLEAN = false
  fecha_creacion : TIMESTAMP = NOW()
}

entity "indicadores_diagnostico" as ID {
  *id : INTEGER <<PK>>
  --
  *diagnostico_id : INTEGER <<FK→diagnosticos>>
  *indicador_id : INTEGER <<FK→indicadores>>
  valor : VARCHAR(20)
  observacion : TEXT
  vulnerado : BOOLEAN = false
}

entity "derechos_vulnerados" as DV {
  *id : INTEGER <<PK>>
  --
  *diagnostico_id : INTEGER <<FK→diagnosticos>>
  *derecho_id : INTEGER <<FK→derechos>>
  severidad : ENUM(severidadvulneracion)
  recomendacion : TEXT
  generado_automaticamente : BOOLEAN = true
}

' ══════════════════════════════════
' PLANEACIÓN
' ══════════════════════════════════

entity "planes_restitucion" as PR {
  *id : INTEGER <<PK>>
  --
  *caso_nna_id : INTEGER <<FK→nna_casos>>
  *objetivo : TEXT
  derechos_afectados : JSON
  responsable_id : INTEGER <<FK→users>>
  fecha_inicio : DATE
  fecha_termino : DATE
  estado : ENUM(estadoplan)
  observaciones : TEXT
  fecha_creacion : TIMESTAMP = NOW()
  fecha_actualizacion : TIMESTAMP = NOW()
}

entity "medidas_restitucion" as MR {
  *id : INTEGER <<PK>>
  --
  *plan_id : INTEGER <<FK→planes_restitucion>>
  *tipo : ENUM(tipomedida)
  *descripcion : TEXT
  responsable_id : INTEGER <<FK→users>>
  actor_id : INTEGER <<FK→actores>>
  recursos_requeridos : TEXT
  estado : ENUM(estadomedida)
  porcentaje_avance : INTEGER = 0
  fecha_inicio : DATE
  fecha_limite : DATE
  fecha_creacion : TIMESTAMP = NOW()
  fecha_actualizacion : TIMESTAMP = NOW()
}

entity "seguimientos_medida" as SM {
  *id : INTEGER <<PK>>
  --
  *medida_id : INTEGER <<FK→medidas_restitucion>>
  registrado_por_id : INTEGER <<FK→users>>
  *fecha_seguimiento : DATE
  *descripcion_avance : TEXT
  porcentaje_cumplimiento : INTEGER = 0
  observaciones : TEXT
  evidencias : JSON
  fecha_creacion : TIMESTAMP = NOW()
}

' ══════════════════════════════════
' RELACIONES ER
' ══════════════════════════════════

U ||--o{ AL       : genera
U ||--o{ NC       : crea
U ||--o{ DG       : es responsable
U ||--o{ PR       : es responsable
U ||--o{ MR       : es responsable
U ||--o{ SM       : registra

NC ||--o| NT      : tiene
NC ||--o| NDM     : tiene
NC ||--o{ NP      : tiene
NC ||--o{ NRF     : tiene
NC ||--o| NF      : tiene
NC ||--o| NE      : tiene
NC ||--o{ NO      : tiene
NC ||--o{ DG      : tiene
NC ||--o{ PR      : tiene

NP ||--o{ NRF     : es origen de
NP ||--o{ NRF     : es destino de

D  ||--o{ IND     : tiene
D  ||--o{ AS2     : atiende
D  ||--o{ DV      : vulnerado

A  ||--o{ AR      : tiene
A  ||--o{ AH      : tiene
A  ||--o{ AS2     : ofrece
A  ||--o{ MR      : apoya en

AS2 ||--o{ SR     : requiere

DG ||--o{ ID      : evalua
DG ||--o{ DV      : genera

IND ||--o{ ID     : evaluado en

PR ||--o{ MR      : contiene
MR ||--o{ SM      : registra

@enduml
```

---

## 5.2 Diccionario de Datos

### Tabla: users

| Campo | Tipo | Tamaño | Nulo | PK | FK | Descripción |
|---|---|---|---|---|---|---|
| id | INTEGER | - | NO | SÍ | - | Identificador único auto-incremental del usuario |
| nombre | VARCHAR | 50 | NO | - | - | Nombre de pila del empleado |
| apellido_paterno | VARCHAR | 50 | NO | - | - | Apellido paterno del empleado |
| apellido_materno | VARCHAR | 50 | NO | - | - | Apellido materno del empleado |
| rfc | VARCHAR | 13 | NO | - | - | RFC del empleado (UNIQUE, validado con regex mexicano) |
| curp | VARCHAR | 18 | NO | - | - | CURP del empleado (UNIQUE, 18 caracteres) |
| sexo | VARCHAR | 10 | NO | - | - | Sexo biológico del empleado: 'M', 'F' |
| fecha_nacimiento | DATE | - | NO | - | - | Fecha de nacimiento del empleado |
| edad | INTEGER | - | NO | - | - | Edad calculada del empleado |
| estado | VARCHAR | 50 | NO | - | - | Estado de la República donde vive |
| municipio | VARCHAR | 100 | NO | - | - | Municipio o alcaldía de residencia |
| colonia | VARCHAR | 100 | NO | - | - | Colonia de residencia |
| calle | VARCHAR | 100 | NO | - | - | Nombre de la calle |
| numero | VARCHAR | 20 | NO | - | - | Número exterior |
| codigo_postal | VARCHAR | 5 | NO | - | - | Código postal de 5 dígitos |
| calles_aledanas | TEXT | - | SÍ | - | - | Referencias de calles cercanas |
| tipo_personal | VARCHAR | 20 | NO | - | - | Tipo: 'empleado', 'voluntario' |
| rol | VARCHAR | 30 | NO | - | - | Rol en el sistema: director, coordinador, psicologo, trabajador_social, legal |
| correo | VARCHAR | 100 | NO | - | - | Correo electrónico (UNIQUE, usado para login) |
| password | VARCHAR | 255 | NO | - | - | Hash bcrypt de la contraseña |
| activo | BOOLEAN | - | SÍ | - | - | Estado de activación de la cuenta |
| verificado | BOOLEAN | - | SÍ | - | - | Indica si la cuenta fue verificada por el director |
| foto_perfil | VARCHAR | 500 | SÍ | - | - | Ruta o URL de la foto de perfil |
| fecha_creacion | TIMESTAMP | - | SÍ | - | - | Fecha y hora de registro en el sistema |

### Tabla: nna_casos

| Campo | Tipo | Tamaño | Nulo | PK | FK | Descripción |
|---|---|---|---|---|---|---|
| id | INTEGER | - | NO | SÍ | - | Identificador único del caso NNA |
| nna_nombre | VARCHAR | 200 | NO | - | - | Nombre completo del NNA |
| nna_curp | VARCHAR | 18 | SÍ | - | - | CURP del NNA |
| nna_fecha_nacimiento | DATE | - | SÍ | - | - | Fecha de nacimiento del NNA |
| nna_edad | INTEGER | - | SÍ | - | - | Edad del NNA al momento del registro |
| nna_genero | ENUM | - | SÍ | - | - | Género: masculino, femenino, no_binario, prefiero_no_decir |
| nna_nacionalidad | VARCHAR | 100 | SÍ | - | - | Nacionalidad del NNA |
| nna_estado_civil | VARCHAR | 50 | SÍ | - | - | Estado civil del NNA (relevante para adolescentes) |
| estado | ENUM | - | NO | - | - | Estado del caso: activo, seguimiento, cerrado, archivado |
| creador_id | INTEGER | - | NO | - | users.id | Usuario que creó el caso |
| fecha_creacion | TIMESTAMP | - | SÍ | - | - | Fecha de apertura del caso |
| fecha_actualizacion | TIMESTAMP | - | SÍ | - | - | Última modificación del caso |

### Tabla: nna_tutores

| Campo | Tipo | Tamaño | Nulo | PK | FK | Descripción |
|---|---|---|---|---|---|---|
| id | INTEGER | - | NO | SÍ | - | Identificador único del tutor |
| caso_id | INTEGER | - | NO | - | nna_casos.id | Caso al que pertenece el tutor |
| nombre | VARCHAR | 100 | NO | - | - | Nombre del tutor/responsable legal |
| apellido_paterno | VARCHAR | 100 | SÍ | - | - | Apellido paterno del tutor |
| apellido_materno | VARCHAR | 100 | SÍ | - | - | Apellido materno del tutor |
| curp | VARCHAR | 18 | SÍ | - | - | CURP del tutor |
| rfc | VARCHAR | 13 | SÍ | - | - | RFC del tutor |
| parentesco | VARCHAR | 50 | NO | - | - | Parentesco con el NNA: madre, padre, abuelo/a, tío/a, tutor legal |
| telefono | VARCHAR | 20 | SÍ | - | - | Teléfono de contacto del tutor |
| correo | VARCHAR | 100 | SÍ | - | - | Correo electrónico del tutor |
| direccion | VARCHAR | 300 | SÍ | - | - | Dirección de residencia del tutor |
| ocupacion | VARCHAR | 150 | SÍ | - | - | Ocupación laboral del tutor |
| documento_identificacion | VARCHAR | 50 | SÍ | - | - | Tipo de documento: INE, pasaporte, etc. |
| numero_documento | VARCHAR | 100 | SÍ | - | - | Número del documento de identificación |

### Tabla: nna_datos_medicos

| Campo | Tipo | Tamaño | Nulo | PK | FK | Descripción |
|---|---|---|---|---|---|---|
| id | INTEGER | - | NO | SÍ | - | Identificador único |
| caso_id | INTEGER | - | NO | - | nna_casos.id | Caso al que pertenecen los datos médicos |
| historial_medico | TEXT | - | SÍ | - | - | Descripción del historial médico relevante |
| alergias | TEXT | - | SÍ | - | - | Alergias conocidas del NNA |
| discapacidades | TEXT | - | SÍ | - | - | Discapacidades documentadas |
| tipo_sangre | VARCHAR | 5 | SÍ | - | - | Tipo de sangre: A+, A-, B+, B-, AB+, AB-, O+, O- |
| medico_responsable | VARCHAR | 200 | SÍ | - | - | Nombre del médico tratante |
| institucion_medica | VARCHAR | 200 | SÍ | - | - | Institución médica de atención |
| cartilla_vacunacion | JSON | - | SÍ | - | - | Array de objetos: [{vacuna, fecha, dosis}] |

### Tabla: nna_personas

| Campo | Tipo | Tamaño | Nulo | PK | FK | Descripción |
|---|---|---|---|---|---|---|
| id | INTEGER | - | NO | SÍ | - | Identificador único de la persona familiar |
| caso_id | INTEGER | - | NO | - | nna_casos.id | Caso al que pertenece |
| nombre | VARCHAR | 200 | NO | - | - | Nombre completo de la persona |
| edad | INTEGER | - | SÍ | - | - | Edad de la persona |
| genero | ENUM | - | SÍ | - | - | Género: masculino, femenino, no_binario |
| rol_en_familia | VARCHAR | 100 | SÍ | - | - | Rol: padre, madre, hermano/a, abuelo/a, tío/a, etc. |
| tipo_simbolo | ENUM | - | SÍ | - | - | Símbolo en el familiograma: normal, clave, cuidador, agresor, fallecido |
| observaciones | TEXT | - | SÍ | - | - | Notas clínicas sobre la persona |
| telefono | VARCHAR | 20 | SÍ | - | - | Teléfono de contacto |
| direccion | VARCHAR | 300 | SÍ | - | - | Dirección de residencia |
| ocupacion | VARCHAR | 150 | SÍ | - | - | Ocupación laboral |
| escolaridad | VARCHAR | 100 | SÍ | - | - | Nivel de escolaridad |
| estado_salud | VARCHAR | 200 | SÍ | - | - | Estado de salud conocido |
| vive_con_nna | BOOLEAN | - | SÍ | - | - | Indica si vive en el mismo hogar que el NNA |
| es_responsable_legal | BOOLEAN | - | SÍ | - | - | Indica si es el responsable legal del NNA |
| fecha_creacion | TIMESTAMP | - | SÍ | - | - | Fecha de registro |

### Tabla: nna_relaciones_familiares

| Campo | Tipo | Tamaño | Nulo | PK | FK | Descripción |
|---|---|---|---|---|---|---|
| id | INTEGER | - | NO | SÍ | - | Identificador único de la relación |
| caso_id | INTEGER | - | NO | - | nna_casos.id | Caso al que pertenece |
| persona_origen_id | INTEGER | - | NO | - | nna_personas.id | Persona de origen de la relación |
| persona_destino_id | INTEGER | - | NO | - | nna_personas.id | Persona de destino de la relación |
| tipo_relacion | ENUM | - | NO | - | - | Tipo: biologica, adoptiva, acogimiento, tutela, conflictiva, distante, apoyo |
| descripcion | VARCHAR | 300 | SÍ | - | - | Descripción adicional de la relación |
| bidireccional | BOOLEAN | - | SÍ | - | - | Si la arista del grafo es bidireccional |

### Tabla: nna_familiogramas

| Campo | Tipo | Tamaño | Nulo | PK | FK | Descripción |
|---|---|---|---|---|---|---|
| id | INTEGER | - | NO | SÍ | - | Identificador único del familiograma |
| caso_id | INTEGER | - | NO | - | nna_casos.id | Caso al que pertenece |
| grafo_json | JSON | - | SÍ | - | - | Estado completo del grafo ReactFlow: {nodes:[{id,data,position}], edges:[{id,source,target}]} |
| version | INTEGER | - | SÍ | - | - | Versión del familiograma (incrementa en cada guardado) |
| fecha_creacion | TIMESTAMP | - | SÍ | - | - | Fecha de creación |
| fecha_actualizacion | TIMESTAMP | - | SÍ | - | - | Última actualización |

### Tabla: derechos

| Campo | Tipo | Tamaño | Nulo | PK | FK | Descripción |
|---|---|---|---|---|---|---|
| id | INTEGER | - | NO | SÍ | - | Identificador único del derecho |
| nombre | VARCHAR | 200 | NO | - | - | Nombre del derecho según catálogo |
| descripcion | TEXT | - | SÍ | - | - | Descripción del derecho |
| categoria | ENUM | - | SÍ | - | - | Categoría: salud, educacion, identidad, familia, proteccion, participacion, alimentacion, vivienda, otro |
| articulo_referencia | VARCHAR | 100 | SÍ | - | - | Artículo de ley o tratado internacional de referencia |
| activo | BOOLEAN | - | SÍ | - | - | Si el derecho está activo en el catálogo |

### Tabla: indicadores

| Campo | Tipo | Tamaño | Nulo | PK | FK | Descripción |
|---|---|---|---|---|---|---|
| id | INTEGER | - | NO | SÍ | - | Identificador único del indicador |
| derecho_id | INTEGER | - | NO | - | derechos.id | Derecho al que pertenece este indicador |
| nombre | VARCHAR | 300 | NO | - | - | Enunciado del indicador (pregunta evaluable) |
| descripcion | TEXT | - | SÍ | - | - | Descripción detallada del indicador |
| tipo_evaluacion | VARCHAR | 50 | SÍ | - | - | Tipo de evaluación: si_no, escala, texto |
| activo | BOOLEAN | - | SÍ | - | - | Si el indicador está activo |

### Tabla: actores

| Campo | Tipo | Tamaño | Nulo | PK | FK | Descripción |
|---|---|---|---|---|---|---|
| id | INTEGER | - | NO | SÍ | - | Identificador único del actor |
| nombre | VARCHAR | 300 | NO | - | - | Nombre del actor u organización |
| tipo | ENUM | - | NO | - | - | Tipo: gobierno, civil, empresa, persona_fisica |
| descripcion | TEXT | - | SÍ | - | - | Descripción de la organización y sus actividades |
| direccion | VARCHAR | 300 | SÍ | - | - | Dirección física |
| municipio | VARCHAR | 100 | SÍ | - | - | Municipio o alcaldía de ubicación |
| estado | VARCHAR | 100 | SÍ | - | - | Estado de la República |
| pais | VARCHAR | 100 | SÍ | - | - | País (por defecto México) |
| telefono | VARCHAR | 20 | SÍ | - | - | Teléfono principal de contacto |
| correo | VARCHAR | 100 | SÍ | - | - | Correo electrónico institucional |
| sitio_web | VARCHAR | 200 | SÍ | - | - | Sitio web oficial |
| redes_sociales | JSON | - | SÍ | - | - | Redes sociales: {facebook, twitter, instagram} |
| activo | BOOLEAN | - | SÍ | - | - | Si el actor está activo en el directorio |

### Tabla: actores_servicios

| Campo | Tipo | Tamaño | Nulo | PK | FK | Descripción |
|---|---|---|---|---|---|---|
| id | INTEGER | - | NO | SÍ | - | Identificador único del servicio |
| actor_id | INTEGER | - | NO | - | actores.id | Actor que ofrece el servicio |
| derecho_id | INTEGER | - | SÍ | - | derechos.id | Derecho que atiende este servicio |
| nombre | VARCHAR | 300 | NO | - | - | Nombre del servicio |
| descripcion | TEXT | - | SÍ | - | - | Descripción del servicio |
| tipo | ENUM | - | NO | - | - | Tipo: servicio, producto |
| es_gratuito | BOOLEAN | - | SÍ | - | - | Si el servicio no tiene costo |
| costo | DECIMAL | 10,2 | SÍ | - | - | Costo en pesos mexicanos (si aplica) |
| disponibilidad | VARCHAR | 100 | SÍ | - | - | Descripción de disponibilidad |
| duracion_estimada | VARCHAR | 100 | SÍ | - | - | Duración estimada del servicio |
| activo | BOOLEAN | - | SÍ | - | - | Si el servicio está disponible |

### Tabla: diagnosticos

| Campo | Tipo | Tamaño | Nulo | PK | FK | Descripción |
|---|---|---|---|---|---|---|
| id | INTEGER | - | NO | SÍ | - | Identificador único del diagnóstico |
| caso_nna_id | INTEGER | - | NO | - | nna_casos.id | Caso al que pertenece |
| tipo | ENUM | - | NO | - | - | Tipo: inicial, nna, tutor, entorno |
| fecha | DATE | - | NO | - | - | Fecha en que se realizó el diagnóstico |
| responsable_id | INTEGER | - | SÍ | - | users.id | Usuario que realizó el diagnóstico |
| observaciones | TEXT | - | SÍ | - | - | Observaciones narrativas del diagnóstico |
| completado | BOOLEAN | - | SÍ | - | - | Si el diagnóstico fue completado formalmente |
| fecha_creacion | TIMESTAMP | - | SÍ | - | - | Fecha de registro en el sistema |

### Tabla: indicadores_diagnostico

| Campo | Tipo | Tamaño | Nulo | PK | FK | Descripción |
|---|---|---|---|---|---|---|
| id | INTEGER | - | NO | SÍ | - | Identificador único de la evaluación |
| diagnostico_id | INTEGER | - | NO | - | diagnosticos.id | Diagnóstico al que pertenece |
| indicador_id | INTEGER | - | NO | - | indicadores.id | Indicador evaluado |
| valor | VARCHAR | 20 | SÍ | - | - | Valor de la evaluación: 'si', 'no', 'parcial' |
| observacion | TEXT | - | SÍ | - | - | Observación específica sobre el indicador |
| vulnerado | BOOLEAN | - | SÍ | - | - | Si este indicador fue marcado como vulnerado |

### Tabla: derechos_vulnerados

| Campo | Tipo | Tamaño | Nulo | PK | FK | Descripción |
|---|---|---|---|---|---|---|
| id | INTEGER | - | NO | SÍ | - | Identificador único |
| diagnostico_id | INTEGER | - | NO | - | diagnosticos.id | Diagnóstico que generó este registro |
| derecho_id | INTEGER | - | NO | - | derechos.id | Derecho que fue vulnerado |
| severidad | ENUM | - | SÍ | - | - | Severidad: leve, moderada, grave, critica |
| recomendacion | TEXT | - | SÍ | - | - | Recomendación de acción para restituir el derecho |
| generado_automaticamente | BOOLEAN | - | SÍ | - | - | True si fue generado por el sistema; False si fue ingresado manualmente |

### Tabla: planes_restitucion

| Campo | Tipo | Tamaño | Nulo | PK | FK | Descripción |
|---|---|---|---|---|---|---|
| id | INTEGER | - | NO | SÍ | - | Identificador único del plan |
| caso_nna_id | INTEGER | - | NO | - | nna_casos.id | Caso al que pertenece el plan |
| objetivo | TEXT | - | NO | - | - | Objetivo general del plan de restitución |
| derechos_afectados | JSON | - | SÍ | - | - | Array de IDs de derechos afectados: [1, 3, 5] |
| responsable_id | INTEGER | - | SÍ | - | users.id | Usuario coordinador del plan |
| fecha_inicio | DATE | - | SÍ | - | - | Fecha de inicio del plan |
| fecha_termino | DATE | - | SÍ | - | - | Fecha estimada de término |
| estado | ENUM | - | NO | - | - | Estado: borrador, activo, pausado, completado, cancelado |
| observaciones | TEXT | - | SÍ | - | - | Notas adicionales sobre el plan |
| fecha_creacion | TIMESTAMP | - | SÍ | - | - | Fecha de creación |
| fecha_actualizacion | TIMESTAMP | - | SÍ | - | - | Última modificación |

### Tabla: medidas_restitucion

| Campo | Tipo | Tamaño | Nulo | PK | FK | Descripción |
|---|---|---|---|---|---|---|
| id | INTEGER | - | NO | SÍ | - | Identificador único de la medida |
| plan_id | INTEGER | - | NO | - | planes_restitucion.id | Plan al que pertenece |
| tipo | ENUM | - | NO | - | - | Tipo: psicologica, legal, medica, educativa, social, economica, otra |
| descripcion | TEXT | - | NO | - | - | Descripción de la medida a ejecutar |
| responsable_id | INTEGER | - | SÍ | - | users.id | Usuario responsable de ejecutar la medida |
| actor_id | INTEGER | - | SÍ | - | actores.id | Actor externo que apoya la medida |
| recursos_requeridos | TEXT | - | SÍ | - | - | Recursos necesarios para ejecutar la medida |
| estado | ENUM | - | NO | - | - | Estado: pendiente, en_proceso, completada, cancelada |
| porcentaje_avance | INTEGER | - | SÍ | - | - | Porcentaje de cumplimiento (0-100) |
| fecha_inicio | DATE | - | SÍ | - | - | Fecha de inicio de la medida |
| fecha_limite | DATE | - | SÍ | - | - | Fecha límite de cumplimiento |
| fecha_creacion | TIMESTAMP | - | SÍ | - | - | Fecha de creación |
| fecha_actualizacion | TIMESTAMP | - | SÍ | - | - | Última modificación |

### Tabla: seguimientos_medida

| Campo | Tipo | Tamaño | Nulo | PK | FK | Descripción |
|---|---|---|---|---|---|---|
| id | INTEGER | - | NO | SÍ | - | Identificador único del seguimiento |
| medida_id | INTEGER | - | NO | - | medidas_restitucion.id | Medida a la que pertenece el seguimiento |
| registrado_por_id | INTEGER | - | SÍ | - | users.id | Usuario que registró el seguimiento |
| fecha_seguimiento | DATE | - | NO | - | - | Fecha en que se realizó el seguimiento |
| descripcion_avance | TEXT | - | NO | - | - | Descripción narrativa del avance |
| porcentaje_cumplimiento | INTEGER | - | SÍ | - | - | Porcentaje alcanzado en este seguimiento (0-100) |
| observaciones | TEXT | - | SÍ | - | - | Observaciones adicionales |
| evidencias | JSON | - | SÍ | - | - | Lista de evidencias: [{nombre, archivo_path}] |
| fecha_creacion | TIMESTAMP | - | SÍ | - | - | Fecha de registro en el sistema |

### Tabla: audit_logs

| Campo | Tipo | Tamaño | Nulo | PK | FK | Descripción |
|---|---|---|---|---|---|---|
| id | INTEGER | - | NO | SÍ | - | Identificador único del registro de auditoría |
| usuario_id | INTEGER | - | SÍ | - | users.id | Usuario que realizó la acción |
| accion | VARCHAR | 100 | NO | - | - | Nombre de la acción: crear_caso, actualizar_caso, crear_diagnostico, etc. |
| entidad | VARCHAR | 100 | SÍ | - | - | Nombre de la tabla afectada |
| entidad_id | INTEGER | - | SÍ | - | - | ID del registro afectado |
| detalles | JSON | - | SÍ | - | - | Detalles adicionales de la acción en formato JSON |
| fecha | TIMESTAMP | - | SÍ | - | - | Fecha y hora de la acción |

---

## 5.3 Diseño de Consultas

### QueryLogin

| Atributo | Detalle |
|---|---|
| **Nombre** | QueryLogin |
| **Objetivo** | Recuperar los datos de autenticación de un usuario a partir de su correo electrónico |
| **Parámetros** | `correo` VARCHAR(100) |
| **Resultado** | Fila única con id, password hash, rol y estado activo |

```sql
-- QueryLogin
SELECT
    u.id,
    u.correo,
    u.password,
    u.rol,
    u.activo,
    u.nombre,
    u.apellido_paterno
FROM
    users u
WHERE
    u.correo = :correo
LIMIT 1;
```

**Nota:** Se busca por campo indexado UNIQUE. No requiere índice adicional. El resultado puede ser NULL si el correo no existe; en ese caso el servicio retorna HTTP 401.

---

### QueryExpedientePorId

| Atributo | Detalle |
|---|---|
| **Nombre** | QueryExpedientePorId |
| **Objetivo** | Obtener todos los datos de un caso NNA con su tutor y datos médicos |
| **Parámetros** | `caso_id` INTEGER |
| **Resultado** | Objeto complejo con caso + tutor + datos_medicos |

```sql
-- QueryExpedientePorId
SELECT
    nc.id,
    nc.nna_nombre,
    nc.nna_curp,
    nc.nna_fecha_nacimiento,
    nc.nna_edad,
    nc.nna_genero,
    nc.nna_nacionalidad,
    nc.nna_estado_civil,
    nc.estado,
    nc.creador_id,
    nc.fecha_creacion,
    nc.fecha_actualizacion,
    -- Tutor
    nt.id           AS tutor_id,
    nt.nombre       AS tutor_nombre,
    nt.apellido_paterno AS tutor_apellido_paterno,
    nt.parentesco   AS tutor_parentesco,
    nt.telefono     AS tutor_telefono,
    nt.correo       AS tutor_correo,
    -- Datos médicos
    ndm.id          AS medicos_id,
    ndm.historial_medico,
    ndm.alergias,
    ndm.tipo_sangre,
    ndm.cartilla_vacunacion
FROM
    nna_casos nc
    LEFT JOIN nna_tutores nt  ON nt.caso_id = nc.id
    LEFT JOIN nna_datos_medicos ndm ON ndm.caso_id = nc.id
WHERE
    nc.id = :caso_id;
```

---

### QueryCrearExpediente

| Atributo | Detalle |
|---|---|
| **Nombre** | QueryCrearExpediente |
| **Objetivo** | Insertar un nuevo caso NNA en la base de datos |
| **Parámetros** | nna_nombre, nna_curp, nna_fecha_nacimiento, nna_edad, nna_genero, nna_nacionalidad, estado, creador_id |
| **Resultado** | ID del nuevo caso creado |

```sql
-- QueryCrearExpediente
INSERT INTO nna_casos (
    nna_nombre,
    nna_curp,
    nna_fecha_nacimiento,
    nna_edad,
    nna_genero,
    nna_nacionalidad,
    estado,
    creador_id
) VALUES (
    :nna_nombre,
    :nna_curp,
    :nna_fecha_nacimiento,
    :nna_edad,
    :nna_genero,
    :nna_nacionalidad,
    :estado,
    :creador_id
)
RETURNING id, fecha_creacion;
```

---

### QueryActualizarExpediente

| Atributo | Detalle |
|---|---|
| **Nombre** | QueryActualizarExpediente |
| **Objetivo** | Actualizar los campos modificados de un caso NNA existente |
| **Parámetros** | caso_id, campos dinámicos según lo que se modifique |
| **Resultado** | Número de filas afectadas (1) |

```sql
-- QueryActualizarExpediente
UPDATE nna_casos
SET
    nna_nombre          = COALESCE(:nna_nombre, nna_nombre),
    nna_curp            = COALESCE(:nna_curp, nna_curp),
    nna_edad            = COALESCE(:nna_edad, nna_edad),
    nna_genero          = COALESCE(:nna_genero, nna_genero),
    nna_nacionalidad    = COALESCE(:nna_nacionalidad, nna_nacionalidad),
    estado              = COALESCE(:estado, estado),
    fecha_actualizacion = NOW()
WHERE
    id = :caso_id
RETURNING id, fecha_actualizacion;
```

---

### QueryDiagnosticosPorNNA

| Atributo | Detalle |
|---|---|
| **Nombre** | QueryDiagnosticosPorNNA |
| **Objetivo** | Listar todos los diagnósticos registrados para un caso NNA, ordenados del más reciente al más antiguo |
| **Parámetros** | `caso_id` INTEGER |
| **Resultado** | Lista de diagnósticos con nombre del responsable |

```sql
-- QueryDiagnosticosPorNNA
SELECT
    d.id,
    d.tipo,
    d.fecha,
    d.observaciones,
    d.completado,
    d.fecha_creacion,
    u.nombre        AS responsable_nombre,
    u.apellido_paterno AS responsable_apellido,
    u.rol           AS responsable_rol,
    COUNT(dv.id)    AS total_derechos_vulnerados
FROM
    diagnosticos d
    LEFT JOIN users u  ON u.id = d.responsable_id
    LEFT JOIN derechos_vulnerados dv ON dv.diagnostico_id = d.id
WHERE
    d.caso_nna_id = :caso_id
GROUP BY
    d.id, u.nombre, u.apellido_paterno, u.rol
ORDER BY
    d.fecha DESC,
    d.fecha_creacion DESC;
```

---

### QueryDerechosVulnerados

| Atributo | Detalle |
|---|---|
| **Nombre** | QueryDerechosVulnerados |
| **Objetivo** | Obtener el resumen consolidado de derechos vulnerados para un caso, agrupados por derecho y severidad máxima |
| **Parámetros** | `caso_id` INTEGER |
| **Resultado** | Lista de derechos con severidad máxima y recomendación más reciente |

```sql
-- QueryDerechosVulnerados
SELECT
    der.id          AS derecho_id,
    der.nombre      AS derecho_nombre,
    der.categoria   AS derecho_categoria,
    der.articulo_referencia,
    MAX(dv.severidad::text)  AS severidad_maxima,
    COUNT(dv.id)    AS frecuencia,
    (
        SELECT dv2.recomendacion
        FROM derechos_vulnerados dv2
        JOIN diagnosticos d2 ON d2.id = dv2.diagnostico_id
        WHERE dv2.derecho_id = der.id
          AND d2.caso_nna_id = :caso_id
        ORDER BY d2.fecha DESC
        LIMIT 1
    ) AS recomendacion_mas_reciente
FROM
    derechos_vulnerados dv
    JOIN diagnosticos diag ON diag.id = dv.diagnostico_id
    JOIN derechos der ON der.id = dv.derecho_id
WHERE
    diag.caso_nna_id = :caso_id
GROUP BY
    der.id, der.nombre, der.categoria, der.articulo_referencia
ORDER BY
    CASE MAX(dv.severidad::text)
        WHEN 'critica'  THEN 1
        WHEN 'grave'    THEN 2
        WHEN 'moderada' THEN 3
        WHEN 'leve'     THEN 4
    END;
```

---

### QueryActoresPorMunicipio

| Atributo | Detalle |
|---|---|
| **Nombre** | QueryActoresPorMunicipio |
| **Objetivo** | Buscar actores activos en un municipio específico, opcionalmente filtrados por tipo |
| **Parámetros** | `municipio` VARCHAR, `tipo` VARCHAR (opcional) |
| **Resultado** | Lista de actores con conteo de servicios disponibles |

```sql
-- QueryActoresPorMunicipio
SELECT
    a.id,
    a.nombre,
    a.tipo,
    a.descripcion,
    a.municipio,
    a.estado,
    a.telefono,
    a.correo,
    COUNT(s.id) AS total_servicios,
    COUNT(s.id) FILTER (WHERE s.es_gratuito = true) AS servicios_gratuitos
FROM
    actores a
    LEFT JOIN actores_servicios s ON s.actor_id = a.id AND s.activo = true
WHERE
    a.activo = true
    AND a.municipio ILIKE '%' || :municipio || '%'
    AND (:tipo IS NULL OR a.tipo = :tipo)
GROUP BY
    a.id, a.nombre, a.tipo, a.descripcion, a.municipio, a.estado, a.telefono, a.correo
ORDER BY
    a.nombre;
```

---

### QueryServiciosPorDerecho

| Atributo | Detalle |
|---|---|
| **Nombre** | QueryServiciosPorDerecho |
| **Objetivo** | Obtener todos los servicios disponibles que atienden un derecho específico |
| **Parámetros** | `derecho_id` INTEGER, `municipio` VARCHAR (opcional) |
| **Resultado** | Lista de servicios con datos del actor que los ofrece |

```sql
-- QueryServiciosPorDerecho
SELECT
    s.id            AS servicio_id,
    s.nombre        AS servicio_nombre,
    s.descripcion   AS servicio_descripcion,
    s.tipo,
    s.es_gratuito,
    s.costo,
    s.disponibilidad,
    s.duracion_estimada,
    a.id            AS actor_id,
    a.nombre        AS actor_nombre,
    a.tipo          AS actor_tipo,
    a.municipio,
    a.telefono,
    a.correo,
    d.nombre        AS derecho_nombre,
    -- Horarios del actor
    (
        SELECT JSON_AGG(
            JSON_BUILD_OBJECT('dia', h.dia_semana, 'inicio', h.hora_inicio, 'fin', h.hora_fin)
        )
        FROM actores_horarios h
        WHERE h.actor_id = a.id AND h.activo = true
    ) AS horarios
FROM
    actores_servicios s
    JOIN actores a   ON a.id = s.actor_id
    JOIN derechos d  ON d.id = s.derecho_id
WHERE
    s.derecho_id = :derecho_id
    AND s.activo = true
    AND a.activo = true
    AND (:municipio IS NULL OR a.municipio ILIKE '%' || :municipio || '%')
ORDER BY
    a.nombre, s.nombre;
```

---

### QueryPlanesPorNNA

| Atributo | Detalle |
|---|---|
| **Nombre** | QueryPlanesPorNNA |
| **Objetivo** | Obtener todos los planes de restitución de un caso NNA con el porcentaje de avance calculado |
| **Parámetros** | `caso_id` INTEGER |
| **Resultado** | Lista de planes con avance promedio de medidas |

```sql
-- QueryPlanesPorNNA
SELECT
    p.id,
    p.objetivo,
    p.estado,
    p.fecha_inicio,
    p.fecha_termino,
    p.observaciones,
    p.fecha_creacion,
    u.nombre        AS responsable_nombre,
    u.apellido_paterno,
    COUNT(m.id)     AS total_medidas,
    COUNT(m.id) FILTER (WHERE m.estado = 'completada') AS medidas_completadas,
    COALESCE(
        ROUND(AVG(m.porcentaje_avance)),
        0
    )               AS avance_promedio,
    (
        SELECT JSON_AGG(
            JSON_BUILD_OBJECT(
                'id', m2.id,
                'tipo', m2.tipo,
                'descripcion', m2.descripcion,
                'estado', m2.estado,
                'porcentaje_avance', m2.porcentaje_avance,
                'fecha_limite', m2.fecha_limite
            ) ORDER BY m2.fecha_creacion
        )
        FROM medidas_restitucion m2
        WHERE m2.plan_id = p.id
    )               AS medidas
FROM
    planes_restitucion p
    LEFT JOIN users u ON u.id = p.responsable_id
    LEFT JOIN medidas_restitucion m ON m.plan_id = p.id
WHERE
    p.caso_nna_id = :caso_id
GROUP BY
    p.id, p.objetivo, p.estado, p.fecha_inicio, p.fecha_termino,
    p.observaciones, p.fecha_creacion, u.nombre, u.apellido_paterno
ORDER BY
    p.fecha_creacion DESC;
```

---

### QuerySeguimientosPlan

| Atributo | Detalle |
|---|---|
| **Nombre** | QuerySeguimientosPlan |
| **Objetivo** | Obtener el historial de seguimientos de todas las medidas de un plan, ordenados cronológicamente |
| **Parámetros** | `plan_id` INTEGER |
| **Resultado** | Lista de seguimientos con datos del registrador y de la medida |

```sql
-- QuerySeguimientosPlan
SELECT
    sm.id           AS seguimiento_id,
    sm.fecha_seguimiento,
    sm.descripcion_avance,
    sm.porcentaje_cumplimiento,
    sm.observaciones,
    sm.evidencias,
    sm.fecha_creacion,
    m.id            AS medida_id,
    m.tipo          AS medida_tipo,
    m.descripcion   AS medida_descripcion,
    m.estado        AS medida_estado,
    m.porcentaje_avance AS medida_avance_actual,
    u.nombre        AS registrado_por_nombre,
    u.apellido_paterno AS registrado_por_apellido,
    u.rol           AS registrado_por_rol
FROM
    seguimientos_medida sm
    JOIN medidas_restitucion m ON m.id = sm.medida_id
    JOIN planes_restitucion p  ON p.id = m.plan_id
    LEFT JOIN users u ON u.id = sm.registrado_por_id
WHERE
    p.id = :plan_id
ORDER BY
    sm.fecha_seguimiento DESC,
    sm.fecha_creacion DESC;
```

---

### QueryFamiliograma

| Atributo | Detalle |
|---|---|
| **Nombre** | QueryFamiliograma |
| **Objetivo** | Obtener el familiograma de un caso con todas las personas y relaciones para reconstruir el grafo |
| **Parámetros** | `caso_id` INTEGER |
| **Resultado** | Objeto con grafo_json, personas y relaciones |

```sql
-- QueryFamiliograma — Paso 1: Canvas guardado
SELECT
    id,
    caso_id,
    grafo_json,
    version,
    fecha_actualizacion
FROM
    nna_familiogramas
WHERE
    caso_id = :caso_id
ORDER BY version DESC
LIMIT 1;

-- QueryFamiliograma — Paso 2: Personas del caso
SELECT
    id,
    nombre,
    edad,
    genero,
    rol_en_familia,
    tipo_simbolo,
    observaciones,
    vive_con_nna,
    es_responsable_legal
FROM
    nna_personas
WHERE
    caso_id = :caso_id
ORDER BY id;

-- QueryFamiliograma — Paso 3: Relaciones del caso
SELECT
    rf.id,
    rf.persona_origen_id,
    po.nombre AS persona_origen_nombre,
    rf.persona_destino_id,
    pd.nombre AS persona_destino_nombre,
    rf.tipo_relacion,
    rf.descripcion,
    rf.bidireccional
FROM
    nna_relaciones_familiares rf
    JOIN nna_personas po ON po.id = rf.persona_origen_id
    JOIN nna_personas pd ON pd.id = rf.persona_destino_id
WHERE
    rf.caso_id = :caso_id;
```

---

### QueryUsuariosPorRol

| Atributo | Detalle |
|---|---|
| **Nombre** | QueryUsuariosPorRol |
| **Objetivo** | Obtener la lista de usuarios activos con un rol específico (utilizado para asignar responsables en planes y medidas) |
| **Parámetros** | `rol` VARCHAR(30) |
| **Resultado** | Lista de usuarios con id y nombre completo |

```sql
-- QueryUsuariosPorRol
SELECT
    u.id,
    u.nombre,
    u.apellido_paterno,
    u.apellido_materno,
    u.rol,
    u.correo,
    u.municipio,
    u.estado,
    CONCAT(u.nombre, ' ', u.apellido_paterno, ' ', u.apellido_materno) AS nombre_completo
FROM
    users u
WHERE
    u.activo = true
    AND (:rol IS NULL OR u.rol = :rol)
ORDER BY
    u.apellido_paterno, u.nombre;
```

---

## 5.4 Índices y Restricciones

### Índices Definidos

| Tabla | Columna(s) | Tipo | Justificación |
|---|---|---|---|
| users | correo | UNIQUE INDEX | Búsqueda de login |
| users | rfc | UNIQUE INDEX | Validación de unicidad |
| users | curp | UNIQUE INDEX | Validación de unicidad |
| nna_casos | creador_id | INDEX | Filtrado por creador |
| nna_casos | estado | INDEX | Filtrado por estado |
| diagnosticos | caso_nna_id | INDEX | Consulta de diagnósticos por caso |
| diagnosticos | responsable_id | INDEX | Consulta por responsable |
| derechos_vulnerados | diagnostico_id | INDEX | Consulta de derechos por diagnóstico |
| derechos_vulnerados | derecho_id | INDEX | Frecuencia por derecho |
| planes_restitucion | caso_nna_id | INDEX | Planes por caso |
| medidas_restitucion | plan_id | INDEX | Medidas por plan |
| seguimientos_medida | medida_id | INDEX | Seguimientos por medida |
| actores | municipio | INDEX | Búsqueda por municipio |
| actores_servicios | derecho_id | INDEX | Búsqueda por derecho |
| audit_logs | usuario_id | INDEX | Auditoría por usuario |
| audit_logs | fecha | INDEX | Auditoría por periodo |

### Restricciones de Integridad

| Tabla | Restricción | Descripción |
|---|---|---|
| users | UNIQUE(correo) | No pueden existir dos usuarios con el mismo correo |
| users | CHECK(rol IN ('director','coordinador','psicologo','trabajador_social','legal','voluntario')) | Solo roles válidos |
| nna_casos | FK(creador_id) ON DELETE CASCADE | Al eliminar usuario, se eliminan sus casos |
| nna_tutores | FK(caso_id) ON DELETE CASCADE | Al eliminar caso, se elimina el tutor |
| diagnosticos | FK(caso_nna_id) ON DELETE CASCADE | Al eliminar caso, se eliminan sus diagnósticos |
| derechos_vulnerados | FK(diagnostico_id) ON DELETE CASCADE | Al eliminar diagnóstico, se eliminan sus derechos vulnerados |
| medidas_restitucion | CHECK(porcentaje_avance BETWEEN 0 AND 100) | Porcentaje en rango válido |
| seguimientos_medida | CHECK(porcentaje_cumplimiento BETWEEN 0 AND 100) | Porcentaje en rango válido |
| actores_servicios | FK(actor_id) ON DELETE CASCADE | Al eliminar actor, se eliminan sus servicios |
