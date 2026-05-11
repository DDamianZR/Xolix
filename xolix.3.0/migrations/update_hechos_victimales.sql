-- =============================================
-- Migration: Update hechos_victimales with split names, CURP, and consideraciones
-- =============================================

-- Remove old columns (safe — they may not exist in new installs)
ALTER TABLE hechos_victimales DROP COLUMN IF EXISTS nombre_victima;
ALTER TABLE hechos_victimales DROP COLUMN IF EXISTS nombre_menor;

-- Add separated victim name fields
ALTER TABLE hechos_victimales ADD COLUMN IF NOT EXISTS victima_nombres VARCHAR(100);
ALTER TABLE hechos_victimales ADD COLUMN IF NOT EXISTS victima_apellido_paterno VARCHAR(100);
ALTER TABLE hechos_victimales ADD COLUMN IF NOT EXISTS victima_apellido_materno VARCHAR(100);
ALTER TABLE hechos_victimales ADD COLUMN IF NOT EXISTS victima_curp VARCHAR(18);

-- Add separated minor name fields
ALTER TABLE hechos_victimales ADD COLUMN IF NOT EXISTS menor_nombres VARCHAR(100);
ALTER TABLE hechos_victimales ADD COLUMN IF NOT EXISTS menor_apellido_paterno VARCHAR(100);
ALTER TABLE hechos_victimales ADD COLUMN IF NOT EXISTS menor_apellido_materno VARCHAR(100);
ALTER TABLE hechos_victimales ADD COLUMN IF NOT EXISTS menor_curp VARCHAR(18);

-- Add metadata columns
ALTER TABLE hechos_victimales ADD COLUMN IF NOT EXISTS fecha_creacion_expediente TIMESTAMP DEFAULT NOW();
ALTER TABLE hechos_victimales ADD COLUMN IF NOT EXISTS consideraciones TEXT;

SELECT 'Migration complete: hechos_victimales updated with split names, CURP, and consideraciones' AS status;
