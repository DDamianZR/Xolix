-- =============================================
-- Migration: NNA Protection Module tables
-- Xolix v3.0 — Módulo de Protección NNA
-- =============================================

-- Enums
DO $$ BEGIN
    CREATE TYPE genero_nna AS ENUM ('masculino', 'femenino', 'no_binario', 'otro');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
    CREATE TYPE estado_caso_nna AS ENUM ('activo', 'cerrado');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
    CREATE TYPE tipo_simbolo_familiar AS ENUM ('normal', 'clave', 'fallecido', 'cuidador', 'agresor');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

-- Table: nna_casos
CREATE TABLE IF NOT EXISTS nna_casos (
    id SERIAL PRIMARY KEY,
    nna_nombre VARCHAR(200) NOT NULL,
    nna_edad INTEGER,
    nna_genero genero_nna,
    estado estado_caso_nna NOT NULL DEFAULT 'activo',
    creador_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    fecha_creacion TIMESTAMP DEFAULT NOW(),
    fecha_actualizacion TIMESTAMP DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_nna_casos_id ON nna_casos(id);

-- Table: nna_entrevistas
CREATE TABLE IF NOT EXISTS nna_entrevistas (
    id SERIAL PRIMARY KEY,
    caso_id INTEGER UNIQUE NOT NULL REFERENCES nna_casos(id) ON DELETE CASCADE,
    fecha TIMESTAMP DEFAULT NOW(),
    frases_comunicadas JSONB,
    dia_comun JSONB,
    grado_negacion INTEGER DEFAULT 1,
    observaciones_negacion TEXT,
    completada BOOLEAN DEFAULT FALSE,
    proceso_id INTEGER REFERENCES procesos(id) ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS ix_nna_entrevistas_id ON nna_entrevistas(id);

-- Table: nna_personas
CREATE TABLE IF NOT EXISTS nna_personas (
    id SERIAL PRIMARY KEY,
    caso_id INTEGER NOT NULL REFERENCES nna_casos(id) ON DELETE CASCADE,
    nombre VARCHAR(200) NOT NULL,
    edad INTEGER,
    genero genero_nna,
    rol_en_familia VARCHAR(100),
    tipo_simbolo tipo_simbolo_familiar DEFAULT 'normal',
    observaciones TEXT,
    fecha_creacion TIMESTAMP DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_nna_personas_id ON nna_personas(id);

-- Table: nna_familiogramas
CREATE TABLE IF NOT EXISTS nna_familiogramas (
    id SERIAL PRIMARY KEY,
    caso_id INTEGER UNIQUE NOT NULL REFERENCES nna_casos(id) ON DELETE CASCADE,
    grafo_json JSONB,
    imagen_url TEXT,
    fecha_actualizacion TIMESTAMP DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_nna_familiogramas_id ON nna_familiogramas(id);

-- Table: nna_observaciones
CREATE TABLE IF NOT EXISTS nna_observaciones (
    id SERIAL PRIMARY KEY,
    caso_id INTEGER NOT NULL REFERENCES nna_casos(id) ON DELETE CASCADE,
    persona_familiar_id INTEGER NOT NULL REFERENCES nna_personas(id) ON DELETE CASCADE,
    postura VARCHAR(200),
    tono_voz VARCHAR(100),
    expresion_emocional JSONB,
    estado_fisico JSONB,
    nivel_resistencia VARCHAR(100),
    interpretacion_sugerida TEXT,
    registrada_por_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    fecha_creacion TIMESTAMP DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_nna_observaciones_id ON nna_observaciones(id);

SELECT 'NNA Protection Module tables created successfully' AS status;
