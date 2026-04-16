-- Crear el schema principal 
CREATE SCHEMA IF NOT EXISTS dev_workspace;

-- Crear el schema bronze dentro del workspace
CREATE SCHEMA IF NOT EXISTS dev_workspace.bronze;

-- Crear la tabla Delta donde escribirás el streaming
CREATE TABLE IF NOT EXISTS dev_workspace.bronze.raw_spotify_tracks
USING DELTA
LOCATION 's3://aws-data-lake-databricks/tables/bronze/raw_spotify_tracks';
