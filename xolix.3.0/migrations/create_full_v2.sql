-- =============================================
-- Migration: Xolix v3.1 — Módulos completos
-- Ejecutar después de init_db.sql, create_nna.sql
-- y create_familiograma_extended.sql
-- =============================================

-- ─── Ampliar nna_casos ──────────────────────
ALTER TABLE nna_casos
    ADD COLUMN IF NOT EXISTS nna_curp VARCHAR(18),
    ADD COLUMN IF NOT EXISTS nna_fecha_nacimiento DATE,
    ADD COLUMN IF NOT EXISTS nna_nacionalidad VARCHAR(100) DEFAULT 'Mexicana',
    ADD COLUMN IF NOT EXISTS nna_estado_civil VARCHAR(50);

-- ─── Tutor NNA ──────────────────────────────
CREATE TABLE IF NOT EXISTS nna_tutores (
    id SERIAL PRIMARY KEY,
    caso_id INTEGER UNIQUE NOT NULL REFERENCES nna_casos(id) ON DELETE CASCADE,
    nombre VARCHAR(200) NOT NULL,
    apellido_paterno VARCHAR(100),
    apellido_materno VARCHAR(100),
    curp VARCHAR(18),
    rfc VARCHAR(13),
    parentesco VARCHAR(100),
    telefono VARCHAR(20),
    correo VARCHAR(100),
    direccion VARCHAR(300),
    ocupacion VARCHAR(150),
    documento_identificacion VARCHAR(200),
    numero_documento VARCHAR(100),
    fecha_creacion TIMESTAMP DEFAULT NOW(),
    fecha_actualizacion TIMESTAMP DEFAULT NOW()
);

-- ─── Datos Médicos NNA ──────────────────────
CREATE TABLE IF NOT EXISTS nna_datos_medicos (
    id SERIAL PRIMARY KEY,
    caso_id INTEGER UNIQUE NOT NULL REFERENCES nna_casos(id) ON DELETE CASCADE,
    historial_medico TEXT,
    alergias TEXT,
    discapacidades TEXT,
    cartilla_vacunacion JSONB,
    tipo_sangre VARCHAR(10),
    medico_responsable VARCHAR(200),
    institucion_medica VARCHAR(200),
    fecha_ultimo_chequeo DATE,
    fecha_creacion TIMESTAMP DEFAULT NOW(),
    fecha_actualizacion TIMESTAMP DEFAULT NOW()
);

-- ─── Catálogo de Derechos ───────────────────
DO $$ BEGIN
    CREATE TYPE categoria_derecho AS ENUM
        ('salud','educacion','identidad','familia','proteccion','participacion','alimentacion','vivienda','otro');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

CREATE TABLE IF NOT EXISTS derechos (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(200) NOT NULL,
    descripcion TEXT,
    categoria categoria_derecho NOT NULL DEFAULT 'proteccion',
    articulo_referencia VARCHAR(200),
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS indicadores (
    id SERIAL PRIMARY KEY,
    derecho_id INTEGER NOT NULL REFERENCES derechos(id) ON DELETE CASCADE,
    nombre VARCHAR(300) NOT NULL,
    descripcion TEXT,
    tipo_evaluacion VARCHAR(50) DEFAULT 'si_no',
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT NOW()
);

-- ─── Actores ────────────────────────────────
DO $$ BEGIN
    CREATE TYPE tipo_actor AS ENUM ('gobierno','civil','empresa','persona_fisica');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE tipo_servicio_actor AS ENUM ('servicio','producto');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

CREATE TABLE IF NOT EXISTS actores (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(300) NOT NULL,
    tipo tipo_actor NOT NULL,
    descripcion TEXT,
    direccion VARCHAR(300),
    municipio VARCHAR(100),
    estado VARCHAR(100),
    pais VARCHAR(100) DEFAULT 'México',
    telefono VARCHAR(30),
    correo VARCHAR(150),
    sitio_web VARCHAR(300),
    redes_sociales TEXT,
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT NOW(),
    fecha_actualizacion TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS actores_responsables (
    id SERIAL PRIMARY KEY,
    actor_id INTEGER NOT NULL REFERENCES actores(id) ON DELETE CASCADE,
    nombre VARCHAR(200) NOT NULL,
    cargo VARCHAR(150),
    telefono VARCHAR(30),
    correo VARCHAR(150),
    es_principal BOOLEAN DEFAULT FALSE,
    fecha_creacion TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS actores_horarios (
    id SERIAL PRIMARY KEY,
    actor_id INTEGER NOT NULL REFERENCES actores(id) ON DELETE CASCADE,
    dia_semana VARCHAR(20) NOT NULL,
    hora_inicio VARCHAR(10),
    hora_fin VARCHAR(10),
    activo BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS actores_servicios (
    id SERIAL PRIMARY KEY,
    actor_id INTEGER NOT NULL REFERENCES actores(id) ON DELETE CASCADE,
    derecho_id INTEGER REFERENCES derechos(id) ON DELETE SET NULL,
    nombre VARCHAR(300) NOT NULL,
    descripcion TEXT,
    tipo tipo_servicio_actor NOT NULL DEFAULT 'servicio',
    es_gratuito BOOLEAN DEFAULT TRUE,
    costo NUMERIC(10,2),
    disponibilidad VARCHAR(100),
    duracion_estimada VARCHAR(100),
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS servicios_requisitos (
    id SERIAL PRIMARY KEY,
    servicio_id INTEGER NOT NULL REFERENCES actores_servicios(id) ON DELETE CASCADE,
    descripcion VARCHAR(500) NOT NULL,
    procedimiento_acceso TEXT,
    documentacion_requerida TEXT,
    fecha_creacion TIMESTAMP DEFAULT NOW()
);

-- ─── Diagnósticos ───────────────────────────
DO $$ BEGIN
    CREATE TYPE tipo_diagnostico AS ENUM ('inicial','nna','tutor','entorno');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE severidad_vulneracion AS ENUM ('leve','moderada','grave','critica');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

CREATE TABLE IF NOT EXISTS diagnosticos (
    id SERIAL PRIMARY KEY,
    caso_nna_id INTEGER NOT NULL REFERENCES nna_casos(id) ON DELETE CASCADE,
    tipo tipo_diagnostico NOT NULL,
    fecha DATE NOT NULL,
    responsable_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    observaciones TEXT,
    completado BOOLEAN DEFAULT FALSE,
    fecha_creacion TIMESTAMP DEFAULT NOW(),
    fecha_actualizacion TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS diagnosticos_evidencias (
    id SERIAL PRIMARY KEY,
    diagnostico_id INTEGER NOT NULL REFERENCES diagnosticos(id) ON DELETE CASCADE,
    nombre VARCHAR(300) NOT NULL,
    archivo_path VARCHAR(500),
    descripcion TEXT,
    tipo_archivo VARCHAR(50),
    fecha_subida TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS diagnosticos_indicadores (
    id SERIAL PRIMARY KEY,
    diagnostico_id INTEGER NOT NULL REFERENCES diagnosticos(id) ON DELETE CASCADE,
    indicador_id INTEGER NOT NULL REFERENCES indicadores(id) ON DELETE CASCADE,
    valor VARCHAR(100),
    observacion TEXT,
    vulnerado BOOLEAN DEFAULT FALSE,
    fecha_creacion TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS diagnosticos_derechos_vulnerados (
    id SERIAL PRIMARY KEY,
    diagnostico_id INTEGER NOT NULL REFERENCES diagnosticos(id) ON DELETE CASCADE,
    derecho_id INTEGER NOT NULL REFERENCES derechos(id) ON DELETE CASCADE,
    severidad severidad_vulneracion NOT NULL DEFAULT 'moderada',
    recomendacion TEXT,
    generado_automaticamente BOOLEAN DEFAULT FALSE,
    fecha_creacion TIMESTAMP DEFAULT NOW()
);

-- ─── Planes de Restitución ──────────────────
DO $$ BEGIN
    CREATE TYPE estado_plan AS ENUM ('borrador','activo','pausado','completado','cancelado');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE estado_medida AS ENUM ('pendiente','en_proceso','completada','cancelada');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE tipo_medida AS ENUM ('psicologica','legal','medica','educativa','social','economica','otra');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

CREATE TABLE IF NOT EXISTS planes_restitucion (
    id SERIAL PRIMARY KEY,
    caso_nna_id INTEGER NOT NULL REFERENCES nna_casos(id) ON DELETE CASCADE,
    objetivo TEXT NOT NULL,
    derechos_afectados JSONB,
    responsable_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    fecha_inicio DATE,
    fecha_termino DATE,
    estado estado_plan NOT NULL DEFAULT 'borrador',
    observaciones TEXT,
    fecha_creacion TIMESTAMP DEFAULT NOW(),
    fecha_actualizacion TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS medidas_restitucion (
    id SERIAL PRIMARY KEY,
    plan_id INTEGER NOT NULL REFERENCES planes_restitucion(id) ON DELETE CASCADE,
    tipo tipo_medida NOT NULL DEFAULT 'otra',
    descripcion TEXT NOT NULL,
    responsable_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    actor_id INTEGER REFERENCES actores(id) ON DELETE SET NULL,
    recursos_requeridos TEXT,
    estado estado_medida NOT NULL DEFAULT 'pendiente',
    porcentaje_avance INTEGER DEFAULT 0,
    fecha_inicio DATE,
    fecha_limite DATE,
    fecha_creacion TIMESTAMP DEFAULT NOW(),
    fecha_actualizacion TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS seguimientos_medida (
    id SERIAL PRIMARY KEY,
    medida_id INTEGER NOT NULL REFERENCES medidas_restitucion(id) ON DELETE CASCADE,
    registrado_por_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    fecha_seguimiento DATE NOT NULL,
    descripcion_avance TEXT NOT NULL,
    porcentaje_cumplimiento INTEGER DEFAULT 0,
    observaciones TEXT,
    evidencias JSONB,
    fecha_creacion TIMESTAMP DEFAULT NOW()
);

SELECT 'Migración Xolix v3.1 completada' AS status;
