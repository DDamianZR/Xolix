# Retrospectiva — Iteración 2: Módulo Familiograma
**Proyecto:** Xolix 3.0 — Sistema de Gestión para Fundación  
**Equipo:** Xolix Systems  
**Fecha:** Mayo 2026  
**Módulo:** Protección NNA / Familiograma

---

## ¿Qué funcionó bien?

- **División de responsabilidades clara**: Cada integrante tomó un componente definido (backend, frontend, documentación), lo que redujo conflictos de código.
- **Reutilización de componentes**: Los estilos Neomorphic de `index.css` y los componentes base (`Topbar`, `Modal`, `ProtectedRoute`) permitieron desarrollar 5 pantallas nuevas con coherencia visual sin reescribir estilos.
- **ReactFlow como base del familiograma**: La elección previa de `@xyflow/react` permitió que el editor del familiograma escalara fácilmente con nuevos tipos de nodo.
- **Patrón service/router/model bien establecido**: El backend de FastAPI siguió el mismo patrón en los 5 módulos anteriores, lo que hizo que agregar el módulo de relaciones familiares e historial fuera predecible y rápido.
- **Versionado automático del familiograma**: La decisión de guardar un snapshot del grafo antes de cada sobreescritura resultó en una funcionalidad de historial robusta sin esfuerzo adicional del usuario.

---

## ¿Qué se puede mejorar?

- **Testing**: Actualmente solo existen pruebas de integración básicas. Faltan pruebas unitarias para los servicios nuevos (`nna_service.py`), especialmente para `_guardar_en_historial` y `exportar_familiograma`.
- **Validaciones de frontend**: Algunos formularios no tienen validación en tiempo real (solo al submit). Agregar validaciones con feedback inmediato mejoraría la UX.
- **Manejo de errores más específico**: Los `catch` en el frontend deberían mostrar mensajes más descriptivos en lugar de `alert()` genéricos.
- **Responsividad en pantallas pequeñas**: La cuadrícula de la pantalla de resumen colapsa bien, pero el editor de familiograma no es usable en móvil (limitación de ReactFlow).
- **Paginación**: Las listas de observaciones y personas no tienen paginación; en casos con muchos registros esto podría volverse lento.

---

## Cambios implementados respecto a la iteración anterior

| Cambio | Descripción |
|---|---|
| **+2 nuevos modelos** | `RelacionFamiliar` e `HistorialFamiliograma` en la BD |
| **+7 campos en PersonaFamiliar** | telefono, direccion, ocupacion, escolaridad, estado_salud, vive_con_nna, es_responsable_legal |
| **+5 endpoints backend** | relaciones CRUD, historial, restaurar versión, exportar |
| **+5 pantallas frontend** | PersonasFamiliares, RelacionesFamiliares, HistorialFamiliograma, FamiliogramaReport, ResumenCasoNNA |
| **CasoNNADetalle rediseñado** | De tabs simples a hub de módulos con tarjetas |
| **Historial automático** | El familiograma guarda snapshots automáticamente en cada save |
| **Exportación de datos** | JSON completo con caso, personas, relaciones y grafo |
| **Datos de prueba** | 2 casos NNA completos con seed SQL |

---

## Lecciones aprendidas

1. **Diseñar el modelo de datos antes del código**: En iteraciones anteriores se descubrieron campos faltantes durante el desarrollo. Esta vez, analizar el módulo primero (diccionario de datos) evitó migraciones de emergencia.
2. **Las rutas anidadas en React Router son poderosas**: Centralizar todas las rutas NNA en un patrón `/nna/casos/:id/[módulo]` hace que la navegación sea predecible y fácil de extender.
3. **Los snapshots automáticos son baratos y valiosos**: El costo de guardar un JSON en BD antes de cada sobreescritura es mínimo, pero el valor para el usuario (poder "deshacer") es enorme.
4. **La documentación LaTeX requiere tiempo**: Documentar casos de uso, diagramas ER y wireframes toma tanto tiempo como el desarrollo. Hay que planificarlo explícitamente en el cronograma.
5. **Separar la lógica de negocio al service**: El patrón service/router/schema hace que los tests sean posibles y el código más limpio.
