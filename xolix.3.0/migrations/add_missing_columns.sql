-- Migracion: agregar columnas faltantes en tablas existentes

-- nna_personas
ALTER TABLE nna_personas
  ADD COLUMN IF NOT EXISTS telefono VARCHAR(20),
  ADD COLUMN IF NOT EXISTS direccion VARCHAR(300),
  ADD COLUMN IF NOT EXISTS ocupacion VARCHAR(150),
  ADD COLUMN IF NOT EXISTS escolaridad VARCHAR(100),
  ADD COLUMN IF NOT EXISTS estado_salud VARCHAR(200),
  ADD COLUMN IF NOT EXISTS vive_con_nna BOOLEAN DEFAULT FALSE,
  ADD COLUMN IF NOT EXISTS es_responsable_legal BOOLEAN DEFAULT FALSE;

-- nna_relaciones_familiares
ALTER TABLE nna_relaciones_familiares
  ADD COLUMN IF NOT EXISTS bidireccional BOOLEAN DEFAULT TRUE;

-- nna_tutores
ALTER TABLE nna_tutores
  ADD COLUMN IF NOT EXISTS apellido_paterno VARCHAR(100),
  ADD COLUMN IF NOT EXISTS apellido_materno VARCHAR(100),
  ADD COLUMN IF NOT EXISTS numero_documento VARCHAR(100);

-- nna_datos_medicos
ALTER TABLE nna_datos_medicos
  ADD COLUMN IF NOT EXISTS medico_responsable VARCHAR(200),
  ADD COLUMN IF NOT EXISTS institucion_medica VARCHAR(200);
