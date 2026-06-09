# 4. DISEÑO DINÁMICO

El diseño dinámico describe el comportamiento del sistema a través del tiempo. Para cada caso de uso se presenta: descripción, actores involucrados, precondiciones, flujo principal y alternativo, postcondiciones, y el diagrama de secuencia UML 2.x con notación BCE.

Los participantes de cada diagrama siguen el patrón:
- **Actor** → usuario del sistema (figura de palo)
- **Boundary** → interfaz de usuario (React) o endpoint de la API
- **Control** → capa de servicio (service.py)
- **Entity** → modelo ORM (SQLAlchemy)
- **PostgreSQL** → base de datos relacional

---

## 4.1 Caso de Uso: Login

### Descripción
Permite a un empleado de la fundación autenticarse en el sistema mediante correo electrónico y contraseña.

### Actores
- **Actor primario:** Empleado (cualquier rol)

### Precondiciones
- El usuario debe tener una cuenta registrada en el sistema.
- La cuenta debe estar activa (`activo = true`).

### Flujo Principal
1. El usuario ingresa al sistema y visualiza el formulario de inicio de sesión.
2. El usuario escribe su correo electrónico.
3. El usuario escribe su contraseña.
4. El usuario presiona el botón "Iniciar sesión".
5. El sistema valida que el correo y la contraseña no estén vacíos.
6. El sistema busca al usuario en la base de datos por correo.
7. El sistema verifica que la contraseña coincida con el hash almacenado.
8. El sistema genera un JWT con el ID y rol del usuario.
9. El sistema retorna el token al frontend.
10. El frontend almacena el token en localStorage.
11. El sistema redirige al Dashboard.

### Flujos Alternativos

**FA-01: Correo no encontrado**
- Paso 6a: No se encuentra ningún usuario con ese correo.
- El sistema retorna HTTP 401 con mensaje "Credenciales inválidas".
- El frontend muestra el error en el formulario.
- El flujo termina.

**FA-02: Contraseña incorrecta**
- Paso 7a: La contraseña no coincide con el hash almacenado.
- El sistema retorna HTTP 401 con el mismo mensaje genérico "Credenciales inválidas".
- El flujo termina.

**FA-03: Usuario inactivo**
- Paso 7b: El usuario existe pero `activo = false`.
- El sistema retorna HTTP 403 con mensaje "Cuenta desactivada. Contacte al administrador."
- El flujo termina.

### Postcondiciones
- El token JWT queda almacenado en `localStorage` del navegador.
- El usuario es redirigido al Dashboard.
- Si la autenticación falla, el formulario muestra el error correspondiente.

### Diagrama de Secuencia UML

```
@startuml CU_Login

skinparam sequenceArrowThickness 2
skinparam sequenceGroupBorderThickness 2
skinparam backgroundColor #FAFAFA

title Diagrama de Secuencia — CU-01: Login\nPatrón BCE

actor "Empleado" as U
boundary "IULogin\n[:LoginPage.jsx]" as B
control "AccessCtr\n[:auth.py + security.py]" as C
entity "ORMUsuario\n[:models/user.py]" as E
database "PostgreSQL\n[:proyecto_escom]" as DB

activate U

U -> B : 1. accede a la aplicación
activate B

B --> U : 1.1 render(formulario_login)

U -> B : 2. escribe correo electrónico
U -> B : 3. escribe contraseña
U -> B : 4. presiona "Iniciar sesión"

B -> B : 4.1 validar campos no vacíos

alt [campos vacíos]
  B --> U : 4.1.1 mostrar error de validación local
else [campos completos]
  B -> C : 5. POST /api/auth/login\n{correo, password}
  activate C

  C -> C : 5.1 preparar credenciales

  C -> E : 5.2 obtener_por_correo(correo)
  activate E

  E -> DB : 5.2.1 SELECT * FROM users\nWHERE correo = :correo
  activate DB
  DB --> E : 5.2.2 Row | null
  deactivate DB

  E --> C : 5.3 usuario | None
  deactivate E

  alt [usuario == None]
    C --> B : 5.4.1 HTTP 401 {detail: "Credenciales inválidas"}
    B --> U : 5.4.2 mostrar error "Credenciales inválidas"
  else [usuario encontrado]
    C -> C : 5.5 verify_password(password, usuario.password)

    alt [password incorrecto]
      C --> B : 5.5.1 HTTP 401 {detail: "Credenciales inválidas"}
      B --> U : 5.5.2 mostrar error "Credenciales inválidas"
    else [password correcto]
      C -> C : 5.6 verificar activo(usuario.activo)

      alt [usuario inactivo]
        C --> B : 5.6.1 HTTP 403 {detail: "Cuenta desactivada"}
        B --> U : 5.6.2 mostrar error "Cuenta desactivada"
      else [usuario activo]
        C -> C : 5.7 create_access_token\n({user_id, rol, exp})

        opt [auditoria habilitada]
          C -> DB : 5.8 INSERT INTO audit_logs\n(usuario_id, accion="login", ...)
        end

        C --> B : 5.9 HTTP 200\n{access_token, token_type: "bearer"}
        deactivate C

        B -> B : 5.10 localStorage.setItem("token", access_token)
        B -> B : 5.11 decodificar payload JWT
        B --> U : 5.12 navigate("/dashboard")
      end
    end
  end
end

deactivate B
deactivate U

@enduml
```

---

## 4.2 Caso de Uso: Crear Expediente

### Descripción
Permite a un empleado con rol de psicólogo, trabajador social o coordinador registrar un nuevo caso NNA en el sistema.

### Actores
- **Actor primario:** Psicólogo / Trabajador Social / Coordinador

### Precondiciones
- El empleado debe estar autenticado con un rol autorizado.
- El NNA no debe tener ya un expediente abierto en el sistema.

### Flujo Principal
1. El usuario accede al módulo NNA y selecciona "Nuevo Caso".
2. El sistema presenta el formulario de creación.
3. El usuario captura los datos del NNA (nombre, fecha de nacimiento, género, nacionalidad).
4. El usuario captura los datos del tutor/responsable legal.
5. El usuario captura los datos médicos básicos.
6. El usuario presiona "Guardar".
7. El sistema valida todos los campos requeridos.
8. El sistema verifica que no exista duplicado por CURP.
9. El sistema crea el caso NNA.
10. El sistema crea el registro del tutor vinculado al caso.
11. El sistema crea el registro de datos médicos vinculado al caso.
12. El sistema registra la acción en auditoría.
13. El sistema redirige al detalle del nuevo caso.

### Flujos Alternativos

**FA-01: CURP duplicada**
- Paso 8a: Ya existe un caso con la misma CURP.
- El sistema retorna HTTP 409 "Ya existe un caso registrado con esta CURP."

**FA-02: Datos inválidos**
- Paso 7a: Algún campo requerido está vacío o con formato incorrecto.
- Pydantic retorna HTTP 422 con la lista de errores de validación.

### Postcondiciones
- El nuevo caso NNA queda registrado en `nna_casos`.
- El tutor queda registrado en `nna_tutores`.
- Los datos médicos quedan registrados en `nna_datos_medicos`.
- La acción queda registrada en `audit_logs`.

### Diagrama de Secuencia UML

```
@startuml CU_CrearExpediente

title Diagrama de Secuencia — CU-02: Crear Expediente\nPatrón BCE

actor "Coordinador" as U
boundary "IUExpediente\n[:NuevoCasoNNA.jsx]" as B
control "ExpedienteCtr\n[:nna_service.py]" as C
entity "ORMCasoNNA\n[:models/nna.py]" as E
entity "ORMTutorNNA\n[:models/nna.py]" as ET
entity "ORMDatosMedicos\n[:models/nna.py]" as ED
database "PostgreSQL\n[:proyecto_escom]" as DB

activate U

U -> B : 1. navega a /nna/nuevo
activate B
B --> U : 1.1 render(FormularioNuevoCaso)

U -> B : 2. captura datos del NNA
U -> B : 3. captura datos del tutor
U -> B : 4. captura datos médicos
U -> B : 5. presiona "Guardar"

B -> B : 5.1 validar formulario (campos requeridos)

alt [validación local falla]
  B --> U : 5.1.1 mostrar errores de campo
else [formulario válido]

  B -> C : 6. POST /api/nna/casos\n{nna_nombre, nna_curp, nna_edad,\nnna_genero, tutor, datos_medicos}
  activate C

  C -> C : 6.1 verificar rol (psicologo | trabajador_social | coordinador)

  alt [rol no autorizado]
    C --> B : 6.1.1 HTTP 403 Forbidden
    B --> U : 6.1.2 mostrar "Sin permisos"
  else [rol autorizado]

    C -> E : 6.2 verificar_curp_duplicada(nna_curp)
    activate E
    E -> DB : 6.2.1 SELECT id FROM nna_casos\nWHERE nna_curp = :curp
    activate DB
    DB --> E : 6.2.2 id | null
    deactivate DB
    E --> C : 6.3 caso_existente | None
    deactivate E

    alt [caso_existente != None]
      C --> B : 6.3.1 HTTP 409 "CURP duplicada"
      B --> U : 6.3.2 mostrar error de duplicado
    else [sin duplicado]

      C -> E : 6.4 crear_caso(datos, creador_id)
      activate E
      E -> DB : 6.4.1 INSERT INTO nna_casos\n(nna_nombre, nna_curp, nna_edad,\nnna_genero, estado, creador_id)
      activate DB
      DB --> E : 6.4.2 caso.id (nuevo)
      deactivate DB
      E --> C : 6.5 caso: CasoNNA
      deactivate E

      C -> ET : 6.6 crear_tutor(caso_id, datos_tutor)
      activate ET
      ET -> DB : 6.6.1 INSERT INTO nna_tutores\n(caso_id, nombre, parentesco, ...)
      activate DB
      DB --> ET : 6.6.2 tutor.id
      deactivate DB
      ET --> C : 6.7 tutor: TutorNNA
      deactivate ET

      C -> ED : 6.8 crear_datos_medicos(caso_id, datos_medicos)
      activate ED
      ED -> DB : 6.8.1 INSERT INTO nna_datos_medicos\n(caso_id, historial, alergias, ...)
      activate DB
      DB --> ED : 6.8.2 datos.id
      deactivate DB
      ED --> C : 6.9 datos: DatosMedicosNNA
      deactivate ED

      C -> DB : 6.10 INSERT INTO audit_logs\n(usuario_id, accion="crear_caso",\nentidad="nna_casos", entidad_id=caso.id)
      activate DB
      DB --> C : 6.10.1 ok
      deactivate DB

      C -> DB : 6.11 COMMIT
      activate DB
      DB --> C : 6.11.1 ok
      deactivate DB

      C --> B : 6.12 HTTP 201\nCasoNNAResponse {id, nna_nombre, estado, ...}
      deactivate C

      B -> B : 6.13 navigate("/nna/casos/" + caso.id)
      B --> U : 6.14 mostrar mensaje "Caso creado exitosamente"
    end
  end
end

deactivate B
deactivate U

@enduml
```

---

## 4.3 Caso de Uso: Editar Expediente

### Descripción
Permite actualizar los datos de un caso NNA existente.

### Actores
- **Actor primario:** Psicólogo / Trabajador Social / Coordinador / Director

### Precondiciones
- El caso debe existir en el sistema.
- El usuario debe estar autenticado con rol autorizado.

### Flujo Principal
1. El usuario accede al detalle del caso y selecciona "Editar".
2. El sistema carga los datos actuales del caso en el formulario.
3. El usuario modifica los campos deseados.
4. El usuario presiona "Actualizar".
5. El sistema valida los cambios.
6. El sistema actualiza el registro en la base de datos.
7. El sistema registra la acción en auditoría.
8. El sistema retorna los datos actualizados.

### Flujos Alternativos

**FA-01: Caso no encontrado**
- El sistema retorna HTTP 404 "Caso no encontrado."

**FA-02: Sin cambios**
- El sistema aplica la actualización de todas formas (upsert idempotente).

### Postcondiciones
- Los datos del caso quedan actualizados en `nna_casos`.

### Diagrama de Secuencia UML

```
@startuml CU_EditarExpediente

title Diagrama de Secuencia — CU-03: Editar Expediente\nPatrón BCE

actor "Trabajador Social" as U
boundary "IUExpediente\n[:CasoNNADetalle.jsx]" as B
control "ExpedienteCtr\n[:nna_service.py]" as C
entity "ORMCasoNNA\n[:models/nna.py]" as E
database "PostgreSQL\n[:proyecto_escom]" as DB

activate U

U -> B : 1. navega a /nna/casos/:id
activate B

B -> C : 1.1 GET /api/nna/casos/:id
activate C
C -> E : 1.2 obtener_caso(caso_id)
activate E
E -> DB : 1.2.1 SELECT * FROM nna_casos\nWHERE id = :caso_id
activate DB
DB --> E : 1.2.2 caso_data | null
deactivate DB

alt [caso not found]
  E --> C : 1.2.3 None
  C --> B : 1.3 HTTP 404 "Caso no encontrado"
  B --> U : 1.4 mostrar error 404
else [caso encontrado]
  E --> C : 1.2.4 caso: CasoNNA
  deactivate E
  C --> B : 1.3 HTTP 200 CasoNNAResponse
  deactivate C

  B --> U : 1.4 render(FormularioEdicion, datos=caso)

  U -> B : 2. modifica campos del expediente
  U -> B : 3. presiona "Actualizar"

  B -> B : 3.1 construir payload de cambios

  B -> C : 4. PUT /api/nna/casos/:id\n{campos_modificados}
  activate C

  C -> E : 4.1 obtener_caso(caso_id)
  activate E
  E -> DB : 4.1.1 SELECT * FROM nna_casos\nWHERE id = :caso_id
  activate DB
  DB --> E : 4.1.2 caso_actual
  deactivate DB
  E --> C : 4.2 caso_actual: CasoNNA
  deactivate E

  loop [para cada campo modificado]
    C -> C : 4.3 setattr(caso_actual, campo, nuevo_valor)
  end

  C -> E : 4.4 flush() / commit()
  activate E
  E -> DB : 4.4.1 UPDATE nna_casos SET\n campo1=:v1, campo2=:v2\nWHERE id = :caso_id
  activate DB
  DB --> E : 4.4.2 rowcount = 1
  deactivate DB
  E --> C : 4.5 caso_actualizado: CasoNNA
  deactivate E

  C -> DB : 4.6 INSERT INTO audit_logs\n(accion="actualizar_caso", entidad_id=caso_id)
  activate DB
  DB --> C : 4.6.1 ok
  deactivate DB

  C --> B : 4.7 HTTP 200 CasoNNAResponse
  deactivate C

  B --> U : 4.8 mostrar mensaje "Expediente actualizado"
  B --> U : 4.9 refresh datos en pantalla
end

deactivate B
deactivate U

@enduml
```

---

## 4.4 Caso de Uso: Registrar Diagnóstico

### Descripción
Permite a un psicólogo o trabajador social registrar un diagnóstico para un caso NNA, evaluando los indicadores de derechos.

### Actores
- **Actor primario:** Psicólogo / Trabajador Social

### Precondiciones
- El caso NNA debe existir y estar activo.
- Debe existir al menos un indicador en el catálogo.

### Flujo Principal
1. El usuario navega al módulo de Diagnóstico del caso.
2. El sistema carga los tipos de diagnóstico disponibles.
3. El usuario selecciona el tipo de diagnóstico.
4. El sistema carga los indicadores del catálogo agrupados por derecho.
5. El usuario evalúa cada indicador (sí/no/parcial) y anota observaciones.
6. El usuario presiona "Guardar diagnóstico".
7. El sistema crea el registro del diagnóstico.
8. Para cada indicador marcado como vulnerado, el sistema registra el derecho correspondiente como vulnerado.
9. El sistema registra la acción en auditoría.
10. El sistema muestra el diagnóstico guardado con el resumen de derechos vulnerados.

### Flujos Alternativos

**FA-01: Sin indicadores en catálogo**
- El sistema muestra advertencia "El catálogo de indicadores está vacío."

**FA-02: Diagnóstico del mismo tipo ya existente**
- El sistema permite registrar múltiples diagnósticos del mismo tipo.

### Postcondiciones
- El diagnóstico queda en `diagnosticos`.
- Los registros de evaluación quedan en `indicadores_diagnostico`.
- Los derechos vulnerados quedan en `derechos_vulnerados`.

### Diagrama de Secuencia UML

```
@startuml CU_RegistrarDiagnostico

title Diagrama de Secuencia — CU-04: Registrar Diagnóstico\nPatrón BCE

actor "Psicologa" as U
boundary "IUDiagnostico\n[:DiagnosticoPage.jsx]" as B
control "DiagnosticoCtr\n[:diagnostico_service.py]" as C
entity "ORMDiagnostico\n[:models/diagnostico.py]" as ED
entity "ORMIndicadorDiag\n[:models/diagnostico.py]" as EI
entity "ORMDerechoVuln\n[:models/diagnostico.py]" as EV
entity "ORMIndicador\n[:models/catalogo.py]" as EC
database "PostgreSQL\n[:proyecto_escom]" as DB

activate U

U -> B : 1. navega a /nna/casos/:id/diagnostico
activate B

B -> C : 1.1 GET /api/catalogo/indicadores
activate C
C -> EC : 1.1.1 listar_indicadores()
activate EC
EC -> DB : 1.1.2 SELECT i.*, d.nombre as derecho\nFROM indicadores i\nJOIN derechos d ON i.derecho_id = d.id\nWHERE i.activo = true
activate DB
DB --> EC : 1.1.3 List[IndicadorRow]
deactivate DB
EC --> C : 1.1.4 indicadores: List[Indicador]
deactivate EC
C --> B : 1.1.5 HTTP 200 List[IndicadorResponse]
deactivate C

B --> U : 1.2 render(SelectorTipoDiagnostico)
B --> U : 1.3 render(ListaIndicadoresPorDerecho)

U -> B : 2. selecciona tipo = "inicial"
U -> B : 3. escribe observaciones generales

loop [para cada indicador]
  U -> B : 4.N evalua indicador N\n(valor: "si" | "no" | "parcial", vulnerado: bool)
end

U -> B : 5. presiona "Guardar diagnóstico"

B -> C : 6. POST /api/diagnosticos\n{caso_nna_id, tipo, observaciones,\n evaluaciones: [{indicador_id, valor, vulnerado}]}
activate C

C -> ED : 6.1 crear_diagnostico(caso_nna_id, tipo, responsable_id)
activate ED
ED -> DB : 6.1.1 INSERT INTO diagnosticos\n(caso_nna_id, tipo, fecha, responsable_id, observaciones)
activate DB
DB --> ED : 6.1.2 diagnostico.id
deactivate DB
ED --> C : 6.2 diagnostico: Diagnostico
deactivate ED

loop [para cada evaluacion en evaluaciones]
  C -> EI : 6.3.N crear_indicador_evaluacion\n(diagnostico_id, indicador_id, valor, vulnerado)
  activate EI
  EI -> DB : 6.3.N.1 INSERT INTO indicadores_diagnostico\n(diagnostico_id, indicador_id, valor, vulnerado)
  activate DB
  DB --> EI : 6.3.N.2 ok
  deactivate DB
  EI --> C : 6.3.N.3 ok
  deactivate EI
end

C -> EC : 6.4 obtener_derechos_de_indicadores_vulnerados\n(indicadores_vulnerados)
activate EC
EC -> DB : 6.4.1 SELECT DISTINCT derecho_id\nFROM indicadores\nWHERE id IN (:ids_vulnerados)
activate DB
DB --> EC : 6.4.2 List[derecho_id]
deactivate DB
EC --> C : 6.5 derechos_vulnerados_ids: List[int]
deactivate EC

loop [para cada derecho_id en derechos_vulnerados_ids]
  C -> EV : 6.6.N crear_derecho_vulnerado\n(diagnostico_id, derecho_id, severidad, generado_auto=True)
  activate EV
  EV -> DB : 6.6.N.1 INSERT INTO derechos_vulnerados\n(diagnostico_id, derecho_id, severidad, generado_automaticamente)
  activate DB
  DB --> EV : 6.6.N.2 ok
  deactivate DB
  EV --> C : 6.6.N.3 ok
  deactivate EV
end

C -> DB : 6.7 INSERT INTO audit_logs\n(accion="crear_diagnostico", entidad_id=diagnostico.id)
activate DB
DB --> C : 6.7.1 ok
deactivate DB

C -> DB : 6.8 COMMIT
activate DB
DB --> C : 6.8.1 ok
deactivate DB

C --> B : 6.9 HTTP 201 DiagnosticoResponse\n{id, tipo, derechos_vulnerados: [...]}
deactivate C

B --> U : 6.10 mostrar resumen de derechos vulnerados
B --> U : 6.11 render(HistorialDiagnosticos)

deactivate B
deactivate U

@enduml
```

---

## 4.5 Caso de Uso: Determinar Derechos Vulnerados

### Descripción
Permite al equipo consultar el resumen consolidado de derechos vulnerados para un caso NNA, como base para la planeación de la restitución.

### Actores
- **Actor primario:** Coordinador / Psicólogo / Trabajador Social

### Precondiciones
- El caso debe tener al menos un diagnóstico con indicadores evaluados.

### Flujo Principal
1. El usuario accede al módulo de Diagnóstico del caso.
2. El usuario selecciona "Ver derechos vulnerados".
3. El sistema consulta todos los diagnósticos del caso.
4. El sistema agrega los derechos vulnerados por derecho y severidad.
5. El sistema retorna el resumen.
6. El frontend muestra el panel con los derechos vulnerados agrupados.

### Postcondiciones
- El usuario puede visualizar qué derechos están vulnerados con su severidad y recomendación.

### Diagrama de Secuencia UML

```
@startuml CU_DeterminarDerechos

title Diagrama de Secuencia — CU-05: Determinar Derechos Vulnerados\nPatrón BCE

actor "Coordinador" as U
boundary "IUDiagnostico\n[:DiagnosticoPage.jsx]" as B
control "DiagnosticoCtr\n[:diagnostico_service.py]" as C
entity "ORMDerechoVuln\n[:models/diagnostico.py]" as EV
entity "ORMDerecho\n[:models/catalogo.py]" as ED
database "PostgreSQL\n[:proyecto_escom]" as DB

activate U

U -> B : 1. navega a /nna/casos/:id/diagnostico
activate B
B --> U : 1.1 render(PanelDiagnostico)

U -> B : 2. selecciona "Ver derechos vulnerados"

B -> C : 3. GET /api/diagnosticos/caso/:id/derechos-vulnerados
activate C

C -> EV : 3.1 listar_derechos_vulnerados(caso_id)
activate EV
EV -> DB : 3.1.1 SELECT dv.derecho_id, dv.severidad,\n dv.recomendacion, d.nombre, d.categoria,\n COUNT(dv.id) as frecuencia\nFROM derechos_vulnerados dv\nJOIN diagnosticos diag ON dv.diagnostico_id = diag.id\nJOIN derechos d ON dv.derecho_id = d.id\nWHERE diag.caso_nna_id = :caso_id\nGROUP BY dv.derecho_id, dv.severidad, d.nombre, d.categoria,\n dv.recomendacion\nORDER BY dv.severidad DESC
activate DB
DB --> EV : 3.1.2 List[DerechoVulneradoRow]
deactivate DB
EV --> C : 3.2 derechos_vulnerados: List[DerechoVulnerado]
deactivate EV

loop [para cada derecho_vulnerado]
  C -> ED : 3.3.N obtener_derecho(derecho_id)
  activate ED
  ED -> DB : 3.3.N.1 SELECT * FROM derechos\nWHERE id = :derecho_id
  activate DB
  DB --> ED : 3.3.N.2 derecho_data
  deactivate DB
  ED --> C : 3.3.N.3 derecho: Derecho
  deactivate ED

  C -> C : 3.4.N enriquecer(derecho_vulnerado, derecho)
end

C -> C : 3.5 agrupar_por_severidad(derechos_enriquecidos)

C --> B : 3.6 HTTP 200\n{criticos: [...], graves: [...], moderados: [...], leves: [...]}
deactivate C

alt [sin derechos vulnerados]
  B --> U : 4.1 mostrar "No se han registrado derechos vulnerados para este caso"
else [con derechos vulnerados]
  B --> U : 4.2 render(PanelDerechosVulnerados)
  B --> U : 4.3 render(TarjetasPorSeveridad)
  B --> U : 4.4 render(Recomendaciones)
end

deactivate B
deactivate U

@enduml
```

---

## 4.6 Caso de Uso: Buscar Actores

### Descripción
Permite localizar actores (organizaciones, personas) que pueden apoyar la restitución de un derecho específico, filtrando por municipio, tipo y derecho vulnerado.

### Actores
- **Actor primario:** Trabajador Social / Coordinador

### Precondiciones
- Debe existir al menos un actor en el catálogo.

### Flujo Principal
1. El usuario navega a la sección de Actores.
2. El sistema muestra el listado completo de actores activos.
3. El usuario aplica filtros (municipio, tipo, derecho vulnerado).
4. El sistema ejecuta la búsqueda con los filtros aplicados.
5. El sistema retorna la lista filtrada de actores.
6. El usuario selecciona un actor para ver su detalle.
7. El sistema muestra el detalle completo del actor con sus servicios, horarios y requisitos.

### Postcondiciones
- El usuario puede visualizar los actores disponibles para atender el derecho vulnerado.

### Diagrama de Secuencia UML

```
@startuml CU_BuscarActores

title Diagrama de Secuencia — CU-06: Buscar Actores\nPatrón BCE

actor "Trabajador Social" as U
boundary "IUActor\n[:ActoresList.jsx]" as B
control "ActorCtr\n[:actor_service.py]" as C
entity "ORMActor\n[:models/actor.py]" as E
entity "ORMServicio\n[:models/actor.py]" as ES
database "PostgreSQL\n[:proyecto_escom]" as DB

activate U

U -> B : 1. navega a /actores
activate B

B -> C : 1.1 GET /api/actores?activo=true
activate C
C -> E : 1.1.1 listar_actores({})
activate E
E -> DB : 1.1.2 SELECT * FROM actores\nWHERE activo = true\nORDER BY nombre
activate DB
DB --> E : 1.1.3 List[ActorRow]
deactivate DB
E --> C : 1.1.4 actores: List[Actor]
deactivate E
C --> B : 1.1.5 HTTP 200 List[ActorListResponse]
deactivate C

B --> U : 1.2 render(TablaActores, actores=lista)
B --> U : 1.3 render(PanelFiltros)

U -> B : 2. selecciona filtro municipio = "Cuauhtémoc"
U -> B : 3. selecciona filtro derecho = "Derecho a la salud"
U -> B : 4. presiona "Buscar"

B -> C : 5. GET /api/actores\n?municipio=Cuauhtémoc&derecho_id=1
activate C

C -> E : 5.1 listar_actores\n({municipio: "Cuauhtémoc", derecho_id: 1})
activate E
E -> DB : 5.1.1 SELECT DISTINCT a.*\nFROM actores a\nJOIN actores_servicios s ON s.actor_id = a.id\nWHERE a.activo = true\n AND a.municipio ILIKE '%Cuauhtémoc%'\n AND s.derecho_id = 1\nORDER BY a.nombre
activate DB
DB --> E : 5.1.2 List[ActorRow]
deactivate DB
E --> C : 5.2 actores_filtrados: List[Actor]
deactivate E

opt [sin resultados]
  C --> B : 5.3 HTTP 200 []
  B --> U : 5.4 mostrar "No se encontraron actores con esos criterios"
end

C --> B : 5.5 HTTP 200 List[ActorListResponse]
deactivate C

B --> U : 5.6 render(TablaActores actualizada, n_resultados)

U -> B : 6. selecciona actor "DIF Ciudad de México"

B -> C : 7. GET /api/actores/:actor_id
activate C
C -> E : 7.1 obtener_actor(actor_id)
activate E
E -> DB : 7.1.1 SELECT * FROM actores\nWHERE id = :actor_id
activate DB
DB --> E : 7.1.2 actor_data
deactivate DB
E --> C : 7.2 actor: Actor
deactivate E

C -> ES : 7.3 obtener_servicios(actor_id)
activate ES
ES -> DB : 7.3.1 SELECT s.*, d.nombre as derecho,\n r.descripcion as requisito\nFROM actores_servicios s\nLEFT JOIN derechos d ON s.derecho_id = d.id\nLEFT JOIN servicios_requisitos r ON r.servicio_id = s.id\nWHERE s.actor_id = :actor_id
activate DB
DB --> ES : 7.3.2 List[ServicioRow]
deactivate DB
ES --> C : 7.4 servicios: List[ServicioActor]
deactivate ES

C --> B : 7.5 HTTP 200 ActorResponse {datos, servicios, horarios, responsables}
deactivate C

B --> U : 7.6 render(PaginaDetalleActor)

deactivate B
deactivate U

@enduml
```

---

## 4.7 Caso de Uso: Crear Plan de Restitución

### Descripción
Permite al coordinador crear un plan formal de restitución de derechos para un caso NNA, definiendo el objetivo, los derechos afectados y las medidas a tomar.

### Actores
- **Actor primario:** Coordinador / Director

### Precondiciones
- El caso NNA debe tener al menos un derecho vulnerado documentado en un diagnóstico.
- El usuario debe tener rol `coordinador` o `director`.

### Flujo Principal
1. El usuario navega al módulo de Planes del caso.
2. El sistema muestra el formulario de creación de plan.
3. El usuario captura el objetivo del plan.
4. El usuario selecciona los derechos afectados del listado de derechos vulnerados.
5. El usuario define las medidas de restitución (tipo, descripción, responsable, actor, fecha límite).
6. El usuario presiona "Crear Plan".
7. El sistema crea el plan de restitución.
8. El sistema crea cada medida vinculada al plan.
9. El sistema registra la acción en auditoría.
10. El sistema muestra el plan creado con sus medidas.

### Postcondiciones
- El plan queda en `planes_restitucion` con estado `activo`.
- Las medidas quedan en `medidas_restitucion` con estado `pendiente`.

### Diagrama de Secuencia UML

```
@startuml CU_CrearPlan

title Diagrama de Secuencia — CU-07: Crear Plan de Restitución\nPatrón BCE

actor "Coordinador" as U
boundary "IUPlan\n[:PlanesPage.jsx]" as B
control "PlanCtr\n[:plan_service.py]" as C
entity "ORMPlan\n[:models/plan.py]" as EP
entity "ORMMedida\n[:models/plan.py]" as EM
database "PostgreSQL\n[:proyecto_escom]" as DB

activate U

U -> B : 1. navega a /nna/casos/:id/planes
activate B

ref over B, C : CU-05 Determinar Derechos Vulnerados\n(cargar derechos vulnerados del caso)

B --> U : 1.1 render(FormularioPlan)
B --> U : 1.2 render(ListaDerechosVulnerados para seleccionar)

U -> B : 2. captura objetivo del plan
U -> B : 3. selecciona derechos afectados
U -> B : 4. define fecha de inicio y fecha límite

loop [el usuario agrega medidas]
  U -> B : 5.N captura medida N\n(tipo, descripcion, responsable_id, actor_id, fecha_limite)
  B -> B : 5.N.1 agregar medida al estado local
end

U -> B : 6. presiona "Crear Plan"

B -> B : 6.1 validar que hay al menos 1 medida

alt [sin medidas]
  B --> U : 6.1.1 mostrar "Agrega al menos una medida"
else [con medidas]

  B -> C : 7. POST /api/planes\n{caso_nna_id, objetivo, derechos_afectados,\n responsable_id, fecha_inicio, fecha_termino,\n medidas: [{tipo, descripcion, actor_id, ...}]}
  activate C

  C -> C : 7.1 verificar rol (coordinador | director)

  C -> EP : 7.2 crear_plan\n(caso_nna_id, objetivo, derechos_afectados,\n responsable_id, fecha_inicio, fecha_termino)
  activate EP
  EP -> DB : 7.2.1 INSERT INTO planes_restitucion\n(caso_nna_id, objetivo, derechos_afectados,\n responsable_id, fecha_inicio, fecha_termino,\n estado='activo')
  activate DB
  DB --> EP : 7.2.2 plan.id
  deactivate DB
  EP --> C : 7.3 plan: PlanRestitucion
  deactivate EP

  loop [para cada medida en medidas]
    C -> EM : 7.4.N crear_medida\n(plan_id, tipo, descripcion,\n responsable_id, actor_id, fecha_limite)
    activate EM
    EM -> DB : 7.4.N.1 INSERT INTO medidas_restitucion\n(plan_id, tipo, descripcion, responsable_id,\n actor_id, estado='pendiente', porcentaje_avance=0)
    activate DB
    DB --> EM : 7.4.N.2 medida.id
    deactivate DB
    EM --> C : 7.4.N.3 medida: MedidaRestitucion
    deactivate EM
  end

  C -> DB : 7.5 INSERT INTO audit_logs\n(accion="crear_plan", entidad_id=plan.id)
  activate DB
  DB --> C : 7.5.1 ok
  deactivate DB

  C -> DB : 7.6 COMMIT
  activate DB
  DB --> C : 7.6.1 ok
  deactivate DB

  C --> B : 7.7 HTTP 201 PlanResponse\n{id, objetivo, estado, medidas: [...]}
  deactivate C

  B --> U : 7.8 render(DetallePlan con medidas)
  B --> U : 7.9 mostrar "Plan creado correctamente"
end

deactivate B
deactivate U

@enduml
```

---

## 4.8 Caso de Uso: Registrar Seguimiento

### Descripción
Permite registrar el avance real de una medida de restitución, actualizando su porcentaje de cumplimiento.

### Actores
- **Actor primario:** Psicólogo / Trabajador Social / Coordinador (según la medida)

### Precondiciones
- La medida debe existir y estar en estado `pendiente` o `en_proceso`.
- El usuario debe ser el responsable de la medida o tener rol de coordinador/director.

### Flujo Principal
1. El usuario accede al plan y selecciona la medida a actualizar.
2. El usuario presiona "Registrar seguimiento".
3. El sistema muestra el formulario de seguimiento.
4. El usuario captura la descripción del avance, el porcentaje de cumplimiento y observaciones.
5. El usuario presiona "Guardar seguimiento".
6. El sistema crea el registro de seguimiento.
7. El sistema actualiza el porcentaje de avance de la medida.
8. Si el porcentaje es 100%, el sistema cambia el estado de la medida a `completada`.

### Postcondiciones
- El seguimiento queda en `seguimientos_medida`.
- La medida actualiza su `porcentaje_avance` y eventualmente su `estado`.

### Diagrama de Secuencia UML

```
@startuml CU_RegistrarSeguimiento

title Diagrama de Secuencia — CU-08: Registrar Seguimiento\nPatrón BCE

actor "Psicologa" as U
boundary "IUPlan\n[:PlanesPage.jsx]" as B
control "PlanCtr\n[:plan_service.py]" as C
entity "ORMSeguimiento\n[:models/plan.py]" as ES
entity "ORMMedida\n[:models/plan.py]" as EM
database "PostgreSQL\n[:proyecto_escom]" as DB

activate U

U -> B : 1. selecciona medida del plan
activate B

B -> C : 1.1 GET /api/planes/medidas/:medida_id
activate C
C -> EM : 1.1.1 obtener_medida(medida_id)
activate EM
EM -> DB : 1.1.2 SELECT * FROM medidas_restitucion\nWHERE id = :medida_id
activate DB
DB --> EM : 1.1.3 medida_data
deactivate DB
EM --> C : 1.1.4 medida: MedidaRestitucion
deactivate EM
C --> B : 1.1.5 HTTP 200 MedidaResponse
deactivate C

B --> U : 1.2 render(DetalleMedida, barra_avance)
U -> B : 2. presiona "Registrar seguimiento"
B --> U : 2.1 render(FormularioSeguimiento)

U -> B : 3. captura descripcion_avance
U -> B : 4. captura porcentaje_cumplimiento (0-100)
U -> B : 5. captura observaciones (opcional)
U -> B : 6. presiona "Guardar"

B -> B : 6.1 validar porcentaje entre 0 y 100

B -> C : 7. POST /api/planes/medidas/:medida_id/seguimientos\n{descripcion_avance, porcentaje_cumplimiento, observaciones}
activate C

C -> EM : 7.1 verificar_medida_activa(medida_id)
activate EM
EM -> DB : 7.1.1 SELECT estado FROM medidas_restitucion\nWHERE id = :medida_id
activate DB
DB --> EM : 7.1.2 estado
deactivate DB
EM --> C : 7.2 medida.estado
deactivate EM

alt [estado == "cancelada" o "completada"]
  C --> B : 7.2.1 HTTP 400 "No se puede actualizar una medida completada/cancelada"
  B --> U : 7.2.2 mostrar error
else [estado válido]

  C -> ES : 7.3 crear_seguimiento\n(medida_id, registrado_por_id, descripcion, porcentaje)
  activate ES
  ES -> DB : 7.3.1 INSERT INTO seguimientos_medida\n(medida_id, registrado_por_id,\n fecha_seguimiento, descripcion_avance,\n porcentaje_cumplimiento, observaciones)
  activate DB
  DB --> ES : 7.3.2 seguimiento.id
  deactivate DB
  ES --> C : 7.4 seguimiento: SeguimientoMedida
  deactivate ES

  C -> EM : 7.5 actualizar_avance\n(medida_id, nuevo_porcentaje)
  activate EM
  EM -> DB : 7.5.1 UPDATE medidas_restitucion\nSET porcentaje_avance = :porcentaje,\n fecha_actualizacion = NOW()\nWHERE id = :medida_id
  activate DB
  DB --> EM : 7.5.2 ok
  deactivate DB
  EM --> C : 7.6 ok
  deactivate EM

  alt [porcentaje_cumplimiento == 100]
    C -> EM : 7.7 actualizar_estado(medida_id, "completada")
    activate EM
    EM -> DB : 7.7.1 UPDATE medidas_restitucion\nSET estado = 'completada'\nWHERE id = :medida_id
    activate DB
    DB --> EM : 7.7.2 ok
    deactivate DB
    EM --> C : 7.7.3 ok
    deactivate EM
  end

  C -> DB : 7.8 COMMIT
  activate DB
  DB --> C : 7.8.1 ok
  deactivate DB

  C --> B : 7.9 HTTP 201 SeguimientoResponse\n{seguimiento, medida_actualizada}
  deactivate C

  B --> U : 7.10 actualizar barra de avance (porcentaje)
  B --> U : 7.11 mostrar "Seguimiento registrado"

  opt [medida completada]
    B --> U : 7.12 mostrar badge "Medida completada"
  end
end

deactivate B
deactivate U

@enduml
```

---

## 4.9 Caso de Uso: Generar Familiograma

### Descripción
Permite registrar los integrantes del entorno familiar del NNA, establecer relaciones entre ellos y generar la representación gráfica interactiva del familiograma.

### Actores
- **Actor primario:** Psicólogo / Trabajador Social

### Precondiciones
- El caso NNA debe existir y estar activo.

### Flujo Principal
1. El usuario navega al módulo de Familiograma del caso.
2. El sistema carga las personas familiares registradas y el familiograma existente (si hay).
3. El usuario agrega nuevas personas al entorno familiar.
4. El sistema registra cada persona en la base de datos.
5. El usuario establece relaciones entre personas.
6. El sistema registra cada relación en la base de datos.
7. El sistema actualiza automáticamente el canvas de ReactFlow.
8. El usuario posiciona visualmente los nodos en el canvas.
9. El usuario presiona "Guardar familiograma".
10. El sistema guarda el estado JSON del grafo (posición de nodos, aristas visuales).
11. El sistema retorna el familiograma guardado.

### Postcondiciones
- Las personas quedan en `nna_personas`.
- Las relaciones quedan en `nna_relaciones_familiares`.
- El grafo visual queda en `nna_familiogramas` como JSON.

### Diagrama de Secuencia UML

```
@startuml CU_GenerarFamiliograma

title Diagrama de Secuencia — CU-09: Generar Familiograma\nPatrón BCE

actor "Psicologa" as U
boundary "IUFamiliograma\n[:FamiliogramaEditor.jsx]" as B
control "FamiliogramaCtr\n[:nna_service.py]" as C
entity "ORMPersona\n[:models/nna.py]" as EP
entity "ORMRelacion\n[:models/nna.py]" as ER
entity "ORMFamiliograma\n[:models/nna.py]" as EF
database "PostgreSQL\n[:proyecto_escom]" as DB

activate U

U -> B : 1. navega a /nna/casos/:id/familiograma
activate B

B -> C : 1.1 GET /api/nna/casos/:id/personas
activate C
C -> EP : 1.1.1 listar_personas(caso_id)
activate EP
EP -> DB : 1.1.2 SELECT * FROM nna_personas\nWHERE caso_id = :caso_id
activate DB
DB --> EP : 1.1.3 List[PersonaRow]
deactivate DB
EP --> C : 1.1.4 personas: List[PersonaFamiliar]
deactivate EP
C --> B : 1.1.5 HTTP 200 List[PersonaResponse]
deactivate C

B -> C : 1.2 GET /api/nna/casos/:id/familiograma
activate C
C -> EF : 1.2.1 obtener_familiograma(caso_id)
activate EF
EF -> DB : 1.2.2 SELECT * FROM nna_familiogramas\nWHERE caso_id = :caso_id\nORDER BY version DESC LIMIT 1
activate DB
DB --> EF : 1.2.3 familiograma_data | null
deactivate DB
EF --> C : 1.2.4 familiograma | None
deactivate EF
C --> B : 1.2.5 HTTP 200 FamiliogramaResponse | 204
deactivate C

opt [familiograma existente]
  B -> B : 1.3 cargar_grafo_en_canvas(familiograma.grafo_json)
end

B --> U : 1.4 render(CanvasReactFlow, personas, relaciones)

loop [usuario agrega personas]
  U -> B : 2.N llena formulario persona\n(nombre, edad, genero, rol, tipo_simbolo)
  U -> B : 2.N.1 presiona "Agregar persona"

  B -> C : 3.N POST /api/nna/casos/:id/personas\n{nombre, edad, genero, rol_en_familia, tipo_simbolo}
  activate C
  C -> EP : 3.N.1 crear_persona(caso_id, datos)
  activate EP
  EP -> DB : 3.N.2 INSERT INTO nna_personas\n(caso_id, nombre, edad, genero,\n rol_en_familia, tipo_simbolo)
  activate DB
  DB --> EP : 3.N.3 persona.id
  deactivate DB
  EP --> C : 3.N.4 persona: PersonaFamiliar
  deactivate EP
  C --> B : 3.N.5 HTTP 201 PersonaResponse
  deactivate C

  B -> B : 3.N.6 agregar_nodo_canvas(persona)
end

loop [usuario establece relaciones]
  U -> B : 4.N selecciona persona_origen y persona_destino
  U -> B : 4.N.1 selecciona tipo_relacion
  U -> B : 4.N.2 presiona "Crear relación"

  B -> C : 5.N POST /api/nna/casos/:id/relaciones\n{persona_origen_id, persona_destino_id, tipo_relacion}
  activate C
  C -> ER : 5.N.1 crear_relacion(caso_id, datos)
  activate ER
  ER -> DB : 5.N.2 INSERT INTO nna_relaciones_familiares\n(caso_id, persona_origen_id, persona_destino_id,\n tipo_relacion)
  activate DB
  DB --> ER : 5.N.3 relacion.id
  deactivate DB
  ER --> C : 5.N.4 relacion: RelacionFamiliar
  deactivate ER
  C --> B : 5.N.5 HTTP 201 RelacionResponse
  deactivate C

  B -> B : 5.N.6 agregar_arista_canvas(relacion)
end

U -> B : 6. reposiciona nodos en el canvas
U -> B : 7. presiona "Guardar familiograma"

B -> B : 7.1 capturar_estado_grafo() → grafo_json

B -> C : 8. PUT /api/nna/casos/:id/familiograma\n{grafo_json: {nodes: [...], edges: [...]}}
activate C

C -> EF : 8.1 upsert_familiograma(caso_id, grafo_json)
activate EF
EF -> DB : 8.1.1 INSERT INTO nna_familiogramas\n(caso_id, grafo_json, version)\nON CONFLICT (caso_id)\nDO UPDATE SET grafo_json = :grafo_json,\n version = version + 1
activate DB
DB --> EF : 8.1.2 familiograma.id, version
deactivate DB
EF --> C : 8.2 familiograma: Familiograma
deactivate EF

C --> B : 8.3 HTTP 200 FamiliogramaResponse
deactivate C

B --> U : 8.4 mostrar "Familiograma guardado (v" + version + ")"

deactivate B
deactivate U

@enduml
```
