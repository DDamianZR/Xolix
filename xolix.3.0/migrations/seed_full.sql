-- =============================================
-- Seeder completo — Xolix v3.1
-- Ejecutar DESPUÉS de create_full_v2.sql
-- =============================================

-- ─── Derechos ────────────────────────────────
INSERT INTO derechos (nombre, descripcion, categoria, articulo_referencia) VALUES
('Derecho a la salud',         'Acceso a servicios médicos y bienestar físico/mental',     'salud',        'Art. 4 CPEUM'),
('Derecho a la educación',     'Acceso a educación básica obligatoria y gratuita',          'educacion',    'Art. 3 CPEUM'),
('Derecho a la identidad',     'Registro de nacimiento, nombre y nacionalidad',             'identidad',    'Art. 29 CDN'),
('Derecho a la familia',       'Vivir con su familia o en entorno familiar adecuado',       'familia',      'Art. 9 CDN'),
('Protección contra violencia','Protección contra abuso, negligencia y explotación',        'proteccion',   'Art. 19 CDN'),
('Derecho a la alimentación',  'Acceso a alimentos suficientes y nutritivos',              'alimentacion', 'Art. 4 CPEUM'),
('Derecho a la vivienda',      'Acceso a vivienda digna y segura',                         'vivienda',     'Art. 4 CPEUM'),
('Derecho a la participación', 'Expresar opinión en asuntos que le conciernen',            'participacion', 'Art. 12 CDN')
ON CONFLICT DO NOTHING;

-- ─── Indicadores por derecho ──────────────────
-- Salud (id=1)
INSERT INTO indicadores (derecho_id, nombre, descripcion, tipo_evaluacion)
SELECT id, 'Cuenta con cartilla de vacunación actualizada', 'Verifica que las vacunas estén al día', 'si_no'
FROM derechos WHERE nombre = 'Derecho a la salud'
ON CONFLICT DO NOTHING;

INSERT INTO indicadores (derecho_id, nombre, descripcion, tipo_evaluacion)
SELECT id, 'Tiene acceso a atención médica regular', 'Chequeos médicos periódicos', 'si_no'
FROM derechos WHERE nombre = 'Derecho a la salud'
ON CONFLICT DO NOTHING;

INSERT INTO indicadores (derecho_id, nombre, descripcion, tipo_evaluacion)
SELECT id, 'Presenta señales de desnutrición', 'Evaluación nutricional', 'si_no'
FROM derechos WHERE nombre = 'Derecho a la salud'
ON CONFLICT DO NOTHING;

-- Educación (id=2)
INSERT INTO indicadores (derecho_id, nombre, descripcion, tipo_evaluacion)
SELECT id, 'Está inscrito en escuela', 'Verificar matrícula escolar activa', 'si_no'
FROM derechos WHERE nombre = 'Derecho a la educación'
ON CONFLICT DO NOTHING;

INSERT INTO indicadores (derecho_id, nombre, descripcion, tipo_evaluacion)
SELECT id, 'Asiste regularmente a clases', 'Frecuencia de asistencia', 'si_no'
FROM derechos WHERE nombre = 'Derecho a la educación'
ON CONFLICT DO NOTHING;

-- Identidad (id=3)
INSERT INTO indicadores (derecho_id, nombre, descripcion, tipo_evaluacion)
SELECT id, 'Cuenta con acta de nacimiento', 'Documento de identidad civil', 'si_no'
FROM derechos WHERE nombre = 'Derecho a la identidad'
ON CONFLICT DO NOTHING;

INSERT INTO indicadores (derecho_id, nombre, descripcion, tipo_evaluacion)
SELECT id, 'Cuenta con CURP', 'Clave Única de Registro de Población', 'si_no'
FROM derechos WHERE nombre = 'Derecho a la identidad'
ON CONFLICT DO NOTHING;

-- Familia (id=4)
INSERT INTO indicadores (derecho_id, nombre, descripcion, tipo_evaluacion)
SELECT id, 'Vive con al menos un familiar responsable', 'Cohabitación familiar', 'si_no'
FROM derechos WHERE nombre = 'Derecho a la familia'
ON CONFLICT DO NOTHING;

INSERT INTO indicadores (derecho_id, nombre, descripcion, tipo_evaluacion)
SELECT id, 'El entorno familiar es seguro', 'Ausencia de violencia en el hogar', 'si_no'
FROM derechos WHERE nombre = 'Derecho a la familia'
ON CONFLICT DO NOTHING;

-- Protección contra violencia (id=5)
INSERT INTO indicadores (derecho_id, nombre, descripcion, tipo_evaluacion)
SELECT id, 'Ha sufrido maltrato físico', 'Evidencia de maltrato físico', 'si_no'
FROM derechos WHERE nombre = 'Protección contra violencia'
ON CONFLICT DO NOTHING;

INSERT INTO indicadores (derecho_id, nombre, descripcion, tipo_evaluacion)
SELECT id, 'Ha sufrido maltrato psicológico', 'Evidencia de maltrato emocional', 'si_no'
FROM derechos WHERE nombre = 'Protección contra violencia'
ON CONFLICT DO NOTHING;

INSERT INTO indicadores (derecho_id, nombre, descripcion, tipo_evaluacion)
SELECT id, 'Ha sufrido abuso sexual', 'Evaluación de abuso sexual', 'si_no'
FROM derechos WHERE nombre = 'Protección contra violencia'
ON CONFLICT DO NOTHING;

-- Alimentación (id=6)
INSERT INTO indicadores (derecho_id, nombre, descripcion, tipo_evaluacion)
SELECT id, 'Recibe al menos 3 comidas al día', 'Frecuencia de alimentación diaria', 'si_no'
FROM derechos WHERE nombre = 'Derecho a la alimentación'
ON CONFLICT DO NOTHING;

-- ─── Actores de prueba ────────────────────────
INSERT INTO actores (nombre, tipo, descripcion, municipio, estado, telefono, correo) VALUES
('DIF Ciudad de México', 'gobierno', 'Sistema para el Desarrollo Integral de la Familia del CDMX', 'Cuauhtémoc', 'CDMX', '55-1234-5678', 'atencion@dif.cdmx.gob.mx'),
('IMSS', 'gobierno', 'Instituto Mexicano del Seguro Social', 'Cuauhtémoc', 'CDMX', '800-623-2323', 'info@imss.gob.mx'),
('Consejo de la Judicatura Federal', 'gobierno', 'Órgano judicial para procesos federales', 'Cuauhtémoc', 'CDMX', '55-5229-5600', 'contacto@cjf.gob.mx'),
('Casa Alianza México', 'civil', 'Organización que protege y rehabilita menores en situación de riesgo', 'Iztacalco', 'CDMX', '55-5543-5823', 'info@casaalianza.mx'),
('UNICEF México', 'civil', 'Fondo de las Naciones Unidas para la Infancia', 'Miguel Hidalgo', 'CDMX', '55-5131-0990', 'info@unicef.org.mx')
ON CONFLICT DO NOTHING;

-- Servicios para DIF (primer actor insertado)
INSERT INTO actores_servicios (actor_id, nombre, descripcion, tipo, es_gratuito, disponibilidad)
SELECT a.id, 'Apoyo psicológico infantil', 'Atención psicológica para menores víctimas de violencia', 'servicio', TRUE, 'Lunes a Viernes 9-17h'
FROM actores a WHERE a.nombre = 'DIF Ciudad de México'
ON CONFLICT DO NOTHING;

INSERT INTO actores_servicios (actor_id, nombre, descripcion, tipo, es_gratuito, disponibilidad)
SELECT a.id, 'Asesoría legal familiar', 'Orientación jurídica en materia de familia y menores', 'servicio', TRUE, 'Lunes a Viernes 9-15h'
FROM actores a WHERE a.nombre = 'DIF Ciudad de México'
ON CONFLICT DO NOTHING;

-- Horarios DIF
INSERT INTO actores_horarios (actor_id, dia_semana, hora_inicio, hora_fin)
SELECT a.id, d, '09:00', '17:00'
FROM actores a, (VALUES ('lunes'),('martes'),('miércoles'),('jueves'),('viernes')) AS dias(d)
WHERE a.nombre = 'DIF Ciudad de México'
ON CONFLICT DO NOTHING;

SELECT 'Seeders Xolix v3.1 insertados correctamente' AS status;
