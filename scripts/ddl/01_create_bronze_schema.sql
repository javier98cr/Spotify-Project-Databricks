-- Crear el catálogo principal 
CREATE CATALOG IF NOT EXISTS dev_workspace;

-- Crear el schema bronze dentro del catálogo
CREATE SCHEMA IF NOT EXISTS dev_workspace.bronze;

-- NO CORRER
--DROP SCHEMA IF EXISTS dev_workspace.bronze CASCADE;
--DROP CATALOG IF EXISTS dev_workspace CASCADE;