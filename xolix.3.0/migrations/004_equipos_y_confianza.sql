-- Migración 004: Equipos multidisciplinarios + nivel de confianza de colaboradores
-- Ejecutar: psql -U postgres -d proyecto_escom -f migrations/004_equipos_y_confianza.sql

-- 1. Ampliar tabla users con campos de colaboración
ALTER TABLE users
    ADD COLUMN IF NOT EXISTS tipo_colaboracion VARCHAR(20) DEFAULT 'planta'
        CHECK (tipo_colaboracion IN ('planta', 'voluntario')),
    ADD COLUMN IF NOT EXISTS nivel_confianza INTEGER DEFAULT 3
        CHECK (nivel_confianza BETWEEN 1 AND 5),
    ADD COLUMN IF NOT EXISTS fecha_ultima_evaluacion DATE,
    ADD COLUMN IF NOT EXISTS fecha_ingreso DATE DEFAULT CURRENT_DATE;

-- 2. Agregar responsable_id a nna_casos (trabajador_social líder del caso)
ALTER TABLE nna_casos
    ADD COLUMN IF NOT EXISTS responsable_id INTEGER REFERENCES users(id) ON DELETE SET NULL;

-- Retrocompatibilidad: casos existentes quedan sin responsable (NULL)
-- El seed y la lógica lo asignarán a partir de ahora

-- 3. Tabla de miembros del equipo por caso
CREATE TABLE IF NOT EXISTS nna_equipo_caso (
    id               SERIAL PRIMARY KEY,
    caso_id          INTEGER NOT NULL REFERENCES nna_casos(id) ON DELETE CASCADE,
    usuario_id       INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    rol_en_equipo    VARCHAR(50) NOT NULL
        CHECK (rol_en_equipo IN ('psicologo','trabajador_social','legal','medico','voluntario_apoyo','coordinador','otro')),
    asignado_por_id  INTEGER REFERENCES users(id) ON DELETE SET NULL,
    fecha_asignacion TIMESTAMP NOT NULL DEFAULT NOW(),
    activo           BOOLEAN NOT NULL DEFAULT TRUE,
    observaciones    TEXT,
    UNIQUE (caso_id, usuario_id)
);

CREATE INDEX IF NOT EXISTS idx_equipo_caso_id     ON nna_equipo_caso(caso_id);
CREATE INDEX IF NOT EXISTS idx_equipo_usuario_id  ON nna_equipo_caso(usuario_id);
CREATE INDEX IF NOT EXISTS idx_equipo_activo      ON nna_equipo_caso(activo);

-- 4. Tabla de historial de evaluaciones de confianza
CREATE TABLE IF NOT EXISTS evaluaciones_confianza (
    id              SERIAL PRIMARY KEY,
    usuario_id      INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    evaluador_id    INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    nivel_anterior  INTEGER NOT NULL CHECK (nivel_anterior BETWEEN 1 AND 5),
    nivel_nuevo     INTEGER NOT NULL CHECK (nivel_nuevo BETWEEN 1 AND 5),
    justificacion   TEXT NOT NULL,
    fecha           TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_eval_usuario  ON evaluaciones_confianza(usuario_id);
CREATE INDEX IF NOT EXISTS idx_eval_fecha    ON evaluaciones_confianza(fecha DESC);
