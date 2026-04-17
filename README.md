# Spotify Tracks — Pipeline Medallion en Databricks

## Fuente

**Dataset:** [Spotify Tracks Dataset](https://www.kaggle.com/datasets/maharshipandya/-spotify-tracks-dataset/data)  
**Autor:** Maharshi Pandya  
**Plataforma:** Kaggle  
**Formato:** Un solo archivo `.csv`  

Una colección curada de más de 114,000 canciones de Spotify que abarcan 125 géneros, enriquecida con características de audio extraídas de la API Web de Spotify. Cada fila representa una canción e incluye metadatos (artista, álbum, género), junto con atributos de análisis de audio (danceability, energy, tempo, etc.) y métricas de popularidad. 

Los datos del archivo .csv se encuentran en un repositorio S3 bucket en AWS (s3://aws-data-lake-databricks/datasets/)
Para fines de prueba, se creó dentro del mismo bucket de AWS una carpeta `/datasets-tests/`, donde el archivo .csv original se divide en múltiples subarchivos. Esto permite probar el funcionamiento de Auto Loader de forma incremental: primero se carga un archivo, se ejecuta el notebook, luego se agrega un nuevo .csv, y así sucesivamente.
---

## Estructura del repositorio
```
├── notebooks/
│ ├── ingestion/ # Capa bronze — ingesta cruda + configuración de tablas
│ ├── transformation/ # Capa silver — limpieza y tipado
│ ├── analysis/ # Capa gold — modelado en esquema snowflake
│ └── visualization/ # Análisis exploratorio y dashboards
├── tests/
│ └── pyspark/ # Pruebas de transformaciones en PySpark
├── configs/
│ ├── .env/ # Configuración por entorno (dev, staging, prod)
│ └── config.yml # Configuración compartida
├── docs/
│ ├── architecture.md # Diagramas de arquitectura
│ └── usage.md # Cómo ejecutar el pipeline
├── scripts/
│ ├── automation/ # Scripts de automatización y scheduling
│ ├── ddl/ # Scripts de defincion de tablas 
│ └── etl/ # Scripts auxiliares de ETL
└── README.md
```

---

## Esquema de datos

### Columnas crudas (según la fuente)

| Columna | Tipo | Descripción |
|---|---|---|
| `track_id` | string | Identificador único de Spotify para la canción |
| `track_name` | string | Nombre de la canción |
| `artists` | string | Nombre(s) del artista, separados por comas si hay múltiples |
| `album_name` | string | Álbum al que pertenece la canción |
| `track_genre` | string | Género asignado a la canción |
| `popularity` | integer | Puntaje de popularidad de 0 a 100 |
| `duration_ms` | integer | Duración de la canción en milisegundos |
| `explicit` | boolean | Indica si la canción tiene contenido explícito |
| `danceability` | float | Qué tan apta es para bailar (0.0–1.0) |
| `energy` | float | Medida perceptual de intensidad (0.0–1.0) |
| `key` | integer | Tonalidad musical (0 = C, 1 = C#, ..., 11 = B) |
| `loudness` | float | Volumen general en decibelios |
| `mode` | integer | Modalidad — 1 = Mayor, 0 = Menor |
| `speechiness` | float | Presencia de palabras habladas (0.0–1.0) |
| `acousticness` | float | Probabilidad de que la canción sea acústica (0.0–1.0) |
| `instrumentalness` | float | Predice si la canción no tiene voz (0.0–1.0) |
| `liveness` | float | Probabilidad de que haya audiencia en vivo (0.0–1.0) |
| `valence` | float | Positividad musical (0.0–1.0) |
| `tempo` | float | Tempo estimado en BPM |
| `time_signature` | integer | Compás estimado (3–7) |

---

## Arquitectura Medallion

El pipeline sigue una arquitectura Medallion de tres capas sobre Delta Lake.

### Bronze — ingesta cruda
Ingesta el archivo CSV tal cual utilizando Auto Loader en una única tabla Delta. No se aplican transformaciones. Todas las columnas se almacenan como strings. Se agregan columnas de metadatos `_ingested_at` y `_source_file`.

### Silver — limpio y tipado
Aplica casteo de tipos, manejo de nulos, deduplicación por `track_id`, y transformaciones a nivel de campo, incluyendo el parseo de `artists` a un array, el mapeo de `key` y `mode` a valores legibles, y la conversión de `explicit` a booleano. También se aplican reglas básicas de calidad de datos.

### Gold — esquema snowflake
Modela los datos limpios de Silver en un esquema snowflake normalizado listo para consumo analítico. Se generan claves sustitutas (surrogate keys) y los datos se dividen en tablas de hechos y dimensiones. Se aplican restricciones estrictas NOT NULL en todas las columnas clave.

#### Tablas Gold
```
dim_artist          dim_genre
├── artist_id (PK)  ├── genre_id (PK)
└── artist_name     └── genre_name
        ▲                   ▲
        │                   │
   dim_album                │
   ├── album_id (PK)        │
   ├── album_name           │
   └── artist_id (FK)       │
        ▲                   │       dim_audio_features
        │                   │       ├── audio_id (PK)
        │                   │       ├── danceability
        └──── fact_tracks ──┘───── ├── energy
              ├── fact_id (PK)     ├── key
              ├── track_id         ├── loudness
              ├── track_name       ├── mode
              ├── album_id (FK)    ├── speechiness
              ├── artist_id (FK)   ├── acousticness
              ├── genre_id (FK)    ├── instrumentalness
              ├── audio_id (FK) ──▶├── liveness
              ├── popularity       ├── valence
              ├── duration_ms      ├── tempo
              └── explicit         └── time_signature
```
---


