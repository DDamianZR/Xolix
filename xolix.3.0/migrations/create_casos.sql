-- =============================================
-- Migration: Case Management System tables
-- Xolix v3.0 — Case Management Module
-- =============================================

-- Enums
DO $$ BEGIN
    CREATE TYPE estadocaso AS ENUM ('activo', 'seguimiento', 'cerrado', 'urgente');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
    CREATE TYPE nivelriesgo AS ENUM ('bajo', 'medio', 'alto', 'critico');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
    CREATE TYPE areaprofesional AS ENUM ('psicologia', 'legal', 'trabajo_social', 'medico', 'analisis', 'general');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
    CREATE TYPE tipoviolencia AS ENUM ('fisica', 'psicologica', 'sexual', 'abandono', 'negligencia', 'otro');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
    CREATE TYPE permisocaso AS ENUM ('lectura', 'escritura', 'admin_caso');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
    CREATE TYPE categoriadocumento AS ENUM ('legal', 'medico', 'evidencia', 'psicologico', 'social', 'otro');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

-- Table: casos
CREATE TABLE IF NOT EXISTS casos (
    id SERIAL PRIMARY KEY,
    folio VARCHAR(20) UNIQUE NOT NULL,
    titulo VARCHAR(300) NOT NULL,
    descripcion TEXT,
    estado estadocaso NOT NULL DEFAULT 'activo',
    nivel_riesgo nivelriesgo NOT NULL DEFAULT 'medio',
    creador_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    fecha_creacion TIMESTAMP DEFAULT NOW(),
    fecha_actualizacion TIMESTAMP DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_casos_id ON casos(id);

-- Table: hechos_victimales
CREATE TABLE IF NOT EXISTS hechos_victimales (
    id SERIAL PRIMARY KEY,
    caso_id INTEGER UNIQUE NOT NULL REFERENCES casos(id) ON DELETE CASCADE,
    nombre_victima VARCHAR(200),
    nombre_menor VARCHAR(200),
    edad_menor INTEGER,
    fecha_incidente DATE,
    ubicacion VARCHAR(300),
    descripcion_delito TEXT,
    tipo_violencia tipoviolencia,
    referencia_juridica VARCHAR(200),
    referencia_fud VARCHAR(200)
);
CREATE INDEX IF NOT EXISTS ix_hechos_victimales_id ON hechos_victimales(id);

-- Table: caso_participantes
CREATE TABLE IF NOT EXISTS caso_participantes (
    id SERIAL PRIMARY KEY,
    caso_id INTEGER NOT NULL REFERENCES casos(id) ON DELETE CASCADE,
    usuario_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    area areaprofesional NOT NULL,
    permiso permisocaso NOT NULL DEFAULT 'escritura',
    fecha_asignacion TIMESTAMP DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_caso_participantes_id ON caso_participantes(id);

-- Table: notas_caso
CREATE TABLE IF NOT EXISTS notas_caso (
    id SERIAL PRIMARY KEY,
    caso_id INTEGER NOT NULL REFERENCES casos(id) ON DELETE CASCADE,
    autor_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    area areaprofesional NOT NULL DEFAULT 'general',
    contenido TEXT NOT NULL,
    privada BOOLEAN DEFAULT FALSE,
    etiquetas TEXT,
    fecha_creacion TIMESTAMP DEFAULT NOW(),
    fecha_actualizacion TIMESTAMP DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_notas_caso_id ON notas_caso(id);

-- Table: documentos_caso
CREATE TABLE IF NOT EXISTS documentos_caso (
    id SERIAL PRIMARY KEY,
    caso_id INTEGER NOT NULL REFERENCES casos(id) ON DELETE CASCADE,
    subido_por_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    nombre VARCHAR(300) NOT NULL,
    archivo_path VARCHAR(500) NOT NULL,
    tipo_archivo VARCHAR(50) NOT NULL DEFAULT 'pdf',
    categoria categoriadocumento NOT NULL DEFAULT 'otro',
    version INTEGER DEFAULT 1,
    fecha_subida TIMESTAMP DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_documentos_caso_id ON documentos_caso(id);

SELECT 'Case Management tables created successfully' AS status;
