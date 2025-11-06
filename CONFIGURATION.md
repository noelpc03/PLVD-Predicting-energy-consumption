# ⚙️ Guía de Configuración - Variables de Entorno

Este proyecto ahora soporta configuración mediante variables de entorno, eliminando valores hardcodeados y haciendo el sistema más flexible.

## 📋 Configuración Inicial

### Paso 1: Crear archivo de configuración

Copia el archivo de ejemplo y personalízalo según tus necesidades:

```bash
cp .env.example .env
```

### Paso 2: Editar variables

Abre el archivo `.env` y ajusta los valores según tu entorno:

```bash
nano .env
# o
vim .env
```

## 🔧 Variables Disponibles

### Usuario y Proyecto

| Variable | Descripción | Valor por Defecto |
|----------|-------------|-------------------|
| `HDFS_USER` | Usuario de HDFS | `amalia` |
| `HDFS_GROUP` | Grupo de HDFS | `amalia` |
| `PROJECT_NAME` | Nombre del proyecto (usado en paths) | `energy_data` |
| `KAFKA_TOPIC` | Topic de Kafka | `energy_stream` |
| `HIVE_TABLE_NAME` | Nombre de la tabla en Hive | `energy_data` |

### Kafka

| Variable | Descripción | Valor por Defecto |
|----------|-------------|-------------------|
| `KAFKA_BROKER` | Dirección del broker Kafka | `kafka:9092` |

### HDFS

| Variable | Descripción | Valor por Defecto |
|----------|-------------|-------------------|
| `HDFS_NAMENODE` | Hostname del NameNode | `namenode` |
| `HDFS_PORT` | Puerto de HDFS | `9000` |

**Nota:** Los paths se construyen automáticamente como:
- Base: `/user/${HDFS_USER}/${PROJECT_NAME}`
- Streaming: `/user/${HDFS_USER}/${PROJECT_NAME}/streaming`

### Producer

| Variable | Descripción | Valor por Defecto |
|----------|-------------|-------------------|
| `PRODUCER_SEND_INTERVAL` | Segundos entre cada mensaje | `0.5` |
| `PRODUCER_MAX_RETRIES` | Reintentos en caso de error | `3` |
| `PRODUCER_DATASET_PATH` | Ruta al dataset | `data/dataset.txt` |

### Consumer (Spark)

| Variable | Descripción | Valor por Defecto |
|----------|-------------|-------------------|
| `SPARK_CHECKPOINT_LOCATION` | Ubicación de checkpoints | `/tmp/spark-checkpoints` |
| `SPARK_PROCESSING_INTERVAL` | Intervalo de procesamiento (segundos) | `60` |
| `SPARK_APP_NAME` | Nombre de la aplicación Spark | `EnergyDataConsumer` |

### Hive

| Variable | Descripción | Valor por Defecto |
|----------|-------------|-------------------|
| `HIVE_METASTORE_URI` | URI del metastore de Hive | `thrift://hive-metastore:9083` |

### Permisos HDFS

| Variable | Descripción | Valor por Defecto |
|----------|-------------|-------------------|
| `HDFS_USER_PERMISSIONS` | Permisos para directorios de usuario | `777` |
| `HDFS_HIVE_PERMISSIONS` | Permisos para directorios de Hive | `755` |

## 📝 Ejemplos de Configuración

### Ejemplo 1: Cambiar usuario y proyecto

```bash
# .env
HDFS_USER=mi_usuario
HDFS_GROUP=mi_grupo
PROJECT_NAME=mi_proyecto
```

Esto creará los paths:
- `/user/mi_usuario/mi_proyecto/streaming`

### Ejemplo 2: Cambiar velocidad de procesamiento

```bash
# .env
PRODUCER_SEND_INTERVAL=1.0        # Enviar cada 1 segundo
SPARK_PROCESSING_INTERVAL=30       # Procesar cada 30 segundos
```

### Ejemplo 3: Cambiar nombres de topic y tabla

```bash
# .env
KAFKA_TOPIC=consumo_energetico
HIVE_TABLE_NAME=datos_energia
```

## 🔄 Cómo Funciona

### En Python (Producer/Consumer)

Los archivos `config.py` cargan automáticamente las variables de entorno usando `python-dotenv`:

```python
from dotenv import load_dotenv
import os

load_dotenv()  # Carga .env si existe

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "kafka:9092")  # Valor por defecto
```

### En Docker Compose

Docker Compose carga automáticamente el archivo `.env` desde el directorio raíz del proyecto. Las variables están disponibles en todos los servicios.

### En Scripts Bash

El script `init-hdfs.sh` carga las variables manualmente:

```bash
if [ -f "../.env" ]; then
    export $(cat ../.env | grep -v '^#' | xargs)
fi

HDFS_USER=${HDFS_USER:-amalia}  # Valor por defecto
```

## ✅ Verificación

Después de configurar, puedes verificar que las variables se cargan correctamente:

### Ver variables en Producer

```bash
docker exec producer env | grep -E "KAFKA|PRODUCER"
```

### Ver variables en Consumer

```bash
docker exec spark-consumer env | grep -E "HDFS|KAFKA|SPARK|HIVE"
```

### Ver paths creados en HDFS

```bash
docker exec namenode hdfs dfs -ls -R /user/${HDFS_USER}/
```

## 🚨 Notas Importantes

1. **El archivo `.env` NO debe hacerse commit** - Está en `.gitignore`
2. **Usa `.env.example` como template** - Este sí se hace commit
3. **Valores por defecto** - Si no defines una variable, se usa el valor por defecto
4. **Reiniciar servicios** - Después de cambiar `.env`, reinicia los servicios:
   ```bash
   cd docker
   docker compose restart producer spark-consumer
   ```

## 🔍 Troubleshooting

### Las variables no se cargan

1. Verifica que el archivo `.env` existe en el directorio raíz
2. Verifica que no tiene errores de sintaxis (sin espacios alrededor del `=`)
3. Reinicia los contenedores después de cambiar `.env`

### Paths incorrectos en HDFS

1. Verifica que `HDFS_USER` y `PROJECT_NAME` están correctos
2. Ejecuta `init-hdfs.sh` nuevamente:
   ```bash
   cd docker
   ./init-hdfs.sh
   ```

### Variables no disponibles en contenedores

1. Verifica que `docker-compose.yml` tiene `env_file: - ../.env`
2. Reconstruye los contenedores:
   ```bash
   cd docker
   docker compose down
   docker compose up -d --build
   ```

## 📚 Referencias

- [python-dotenv documentation](https://github.com/theskumar/python-dotenv)
- [Docker Compose env_file](https://docs.docker.com/compose/env-file/)

