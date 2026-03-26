-- =============================================
-- Migration: Add priority and deadlines support
-- Xolix v3.0 Enhancement
-- =============================================

-- Proceso: add priority and deadline columns
ALTER TABLE procesos ADD COLUMN IF NOT EXISTS prioridad VARCHAR(10) DEFAULT 'media' NOT NULL;
ALTER TABLE procesos ADD COLUMN IF NOT EXISTS fecha_vencimiento TIMESTAMP NULL;

-- Subtarea: add deadline column
ALTER TABLE subtareas ADD COLUMN IF NOT EXISTS fecha_vencimiento TIMESTAMP NULL;

-- Done!
SELECT 'Migration complete: prioridad + fecha_vencimiento added to procesos and subtareas' AS status;
