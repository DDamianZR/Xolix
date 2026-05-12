-- =============================================
-- Seed: Datos de prueba — Módulo Familiograma
-- Xolix v3.0 — Ejecutar DESPUÉS de la migración
-- Requiere: al menos un usuario con id=1 en users
-- =============================================

-- ── Caso NNA 1 ──────────────────────────────
INSERT INTO nna_casos (nna_nombre, nna_edad, nna_genero, estado, creador_id)
VALUES ('Sofía Martínez Ramírez', 9, 'femenino', 'activo', 1)
ON CONFLICT DO NOTHING;

-- Personas familiares del Caso 1
WITH caso AS (SELECT id FROM nna_casos WHERE nna_nombre = 'Sofía Martínez Ramírez' LIMIT 1)
INSERT INTO nna_personas
    (caso_id, nombre, edad, genero, rol_en_familia, tipo_simbolo, telefono, ocupacion, escolaridad, vive_con_nna, es_responsable_legal, observaciones)
SELECT
    caso.id, nombre, edad, genero::genero_nna, rol, simbolo::tipo_simbolo_familiar,
    telefono, ocupacion, escolaridad, vive, legal, obs
FROM caso, (VALUES
    ('Sofía Martínez Ramírez', 9,  'femenino',   'NNA (Víctima)',      'clave',    '555-0001', 'Estudiante',    '3er grado primaria', true,  true,  'Presenta signos de ansiedad'),
    ('Laura Ramírez González',  34, 'femenino',   'Madre',              'cuidador', '555-0002', 'Empleada doméstica', 'Secundaria', true,  true,  'Principal cuidadora, colaborativa'),
    ('José Martínez Torres',    38, 'masculino',  'Padre (ausente)',    'agresor',  NULL,       'Desconocida',   'Desconocida',      false, false, 'Presunto agresor, orden de alejamiento'),
    ('Elena Ramírez Vda.',      62, 'femenino',   'Abuela materna',    'normal',   '555-0003', 'Jubilada',      'Primaria incompleta', true, false, 'Apoyo emocional importante'),
    ('Carlos Martínez Rojas',   16, 'masculino',  'Hermano mayor',     'normal',   NULL,       'Estudiante',    'Preparatoria',     true,  false, 'Relación protectora con la NNA')
) AS t(nombre, edad, genero, rol, simbolo, telefono, ocupacion, escolaridad, vive, legal, obs);

-- Familiograma del Caso 1
WITH caso AS (SELECT id FROM nna_casos WHERE nna_nombre = 'Sofía Martínez Ramírez' LIMIT 1)
INSERT INTO nna_familiogramas (caso_id, grafo_json)
SELECT caso.id, '{"nodes": [], "edges": []}'::jsonb
FROM caso
ON CONFLICT DO NOTHING;

-- Relaciones del Caso 1
WITH
  caso AS (SELECT id FROM nna_casos WHERE nna_nombre = 'Sofía Martínez Ramírez' LIMIT 1),
  sofia      AS (SELECT id FROM nna_personas WHERE nombre = 'Sofía Martínez Ramírez' LIMIT 1),
  laura      AS (SELECT id FROM nna_personas WHERE nombre = 'Laura Ramírez González' LIMIT 1),
  jose       AS (SELECT id FROM nna_personas WHERE nombre = 'José Martínez Torres' LIMIT 1),
  elena      AS (SELECT id FROM nna_personas WHERE nombre = 'Elena Ramírez Vda.' LIMIT 1),
  carlos     AS (SELECT id FROM nna_personas WHERE nombre = 'Carlos Martínez Rojas' LIMIT 1)
INSERT INTO nna_relaciones_familiares (caso_id, persona_origen_id, persona_destino_id, tipo_relacion, descripcion, bidireccional)
VALUES
  ((SELECT id FROM caso), (SELECT id FROM sofia), (SELECT id FROM laura), 'biologica',         'Hija-Madre biológica',                true),
  ((SELECT id FROM caso), (SELECT id FROM sofia), (SELECT id FROM jose),  'conflictiva',        'Hija-Padre, relación conflictiva/abuso', false),
  ((SELECT id FROM caso), (SELECT id FROM sofia), (SELECT id FROM elena), 'emocional_positiva', 'Nieta-Abuela, relación de apoyo',     true),
  ((SELECT id FROM caso), (SELECT id FROM sofia), (SELECT id FROM carlos),'protectora',         'Hermana menor-Hermano protector',     true),
  ((SELECT id FROM caso), (SELECT id FROM laura), (SELECT id FROM jose),  'separacion',         'Pareja separada / orden de alejamiento', false),
  ((SELECT id FROM caso), (SELECT id FROM laura), (SELECT id FROM elena), 'biologica',          'Hija-Madre biológica',                true);

-- Entrevista del Caso 1
WITH caso AS (SELECT id FROM nna_casos WHERE nna_nombre = 'Sofía Martínez Ramírez' LIMIT 1)
INSERT INTO nna_entrevistas (caso_id, grado_negacion, observaciones_negacion, completada,
    frases_comunicadas, dia_comun)
SELECT
    caso.id, 2,
    'La madre reconoce la situación pero solicita tiempo antes de tomar medidas formales.',
    true,
    '[{"id":"f1","texto":"Me siento segura en casa","comunicada":false,"notas":"Negación por miedo"},{"id":"f2","texto":"Quiero ir a la escuela todos los días","comunicada":true,"notas":""},{"id":"f3","texto":"Me gusta jugar con Carlos","comunicada":true,"notas":"Vínculo positivo con hermano"}]'::jsonb,
    '{"quien_despierta":"La madre","rutina_matutina":"Desayuno en familia con abuela","cuidador_dia":"Abuela materna después de escuela","relaciones_externas":"Vecinas de confianza","nna_es_central":"si","adulto_dificultad":"si","personas_mencionadas":["Laura","Elena","Carlos"]}'::jsonb
FROM caso
ON CONFLICT DO NOTHING;

-- ── Caso NNA 2 ──────────────────────────────
INSERT INTO nna_casos (nna_nombre, nna_edad, nna_genero, estado, creador_id)
VALUES ('Emilio Vega Sánchez', 12, 'masculino', 'activo', 1)
ON CONFLICT DO NOTHING;

WITH caso AS (SELECT id FROM nna_casos WHERE nna_nombre = 'Emilio Vega Sánchez' LIMIT 1)
INSERT INTO nna_personas
    (caso_id, nombre, edad, genero, rol_en_familia, tipo_simbolo, ocupacion, vive_con_nna, es_responsable_legal)
SELECT
    caso.id, nombre, edad, genero::genero_nna, rol, simbolo::tipo_simbolo_familiar,
    ocupacion, vive, legal
FROM caso, (VALUES
    ('Emilio Vega Sánchez',  12, 'masculino', 'NNA',            'clave',    'Estudiante',       true,  false),
    ('Roberto Vega Fuentes', 45, 'masculino', 'Padre',          'cuidador', 'Albañil',          true,  true),
    ('Miriam Sánchez Ortiz', 42, 'femenino',  'Madre fallecida','fallecido','Ama de casa (†)',  false, false),
    ('Ana Vega Fuentes',     20, 'femenino',  'Hermana mayor',  'normal',   'Empleada',         false, false)
) AS t(nombre, edad, genero, rol, simbolo, ocupacion, vive, legal);

WITH caso AS (SELECT id FROM nna_casos WHERE nna_nombre = 'Emilio Vega Sánchez' LIMIT 1)
INSERT INTO nna_familiogramas (caso_id, grafo_json)
SELECT caso.id, '{"nodes": [], "edges": []}'::jsonb
FROM caso ON CONFLICT DO NOTHING;

SELECT 'Seed data for Familiograma module inserted successfully' AS status;
