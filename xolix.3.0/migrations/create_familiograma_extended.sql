-- =============================================
-- Migration: Familiograma Extended Tables
-- Xolix v3.0 — Módulo Familiograma (Iteración 2)
-- =============================================

-- Enum: tipos de relación familiar
DO $$ BEGIN
    CREATE TYPE tipo_relacion_familiar AS ENUM (
        'biologica',
        'legal',
        'emocional_positiva',
        'conflictiva',
        'protectora',
        'dependencia',
        'separacion',
        'desconocida'
    );
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

-- Extensión de nna_personas: campos adicionales de contacto y contexto
ALTER TABLE nna_personas
    ADD COLUMN IF NOT EXISTS telefono VARCHAR(20),
    ADD COLUMN IF NOT EXISTS direccion VARCHAR(300),
    ADD COLUMN IF NOT EXISTS ocupacion VARCHAR(150),
    ADD COLUMN IF NOT EXISTS escolaridad VARCHAR(100),
    ADD COLUMN IF NOT EXISTS estado_salud VARCHAR(200),
    ADD COLUMN IF NOT EXISTS vive_con_nna BOOLEAN DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS es_responsable_legal BOOLEAN DEFAULT FALSE;

-- Table: nna_relaciones_familiares
-- Representa aristas tipificadas entre personas del familiograma
CREATE TABLE IF NOT EXISTS nna_relaciones_familiares (
    id SERIAL PRIMARY KEY,
    caso_id INTEGER NOT NULL REFERENCES nna_casos(id) ON DELETE CASCADE,
    persona_origen_id INTEGER NOT NULL REFERENCES nna_personas(id) ON DELETE CASCADE,
    persona_destino_id INTEGER NOT NULL REFERENCES nna_personas(id) ON DELETE CASCADE,
    tipo_relacion tipo_relacion_familiar NOT NULL DEFAULT 'biologica',
    descripcion TEXT,
    bidireccional BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_nna_relaciones_caso ON nna_relaciones_familiares(caso_id);
CREATE INDEX IF NOT EXISTS ix_nna_relaciones_id ON nna_relaciones_familiares(id);

-- Table: nna_historial_familiograma
-- Versionado automático del grafo JSON al guardar
CREATE TABLE IF NOT EXISTS nna_historial_familiograma (
    id SERIAL PRIMARY KEY,
    familiograma_id INTEGER NOT NULL REFERENCES nna_familiogramas(id) ON DELETE CASCADE,
    caso_id INTEGER NOT NULL REFERENCES nna_casos(id) ON DELETE CASCADE,
    version INTEGER NOT NULL DEFAULT 1,
    grafo_json JSONB,
    modificado_por_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    notas_version VARCHAR(500),
    fecha TIMESTAMP DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_nna_historial_familiograma_id ON nna_historial_familiograma(id);
CREATE INDEX IF NOT EXISTS ix_nna_historial_caso ON nna_historial_familiograma(caso_id);

SELECT 'Familiograma Extended tables created successfully' AS status;
