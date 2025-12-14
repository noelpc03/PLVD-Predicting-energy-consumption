# config.py - Configuración del Consumer
import os

# Intentar cargar variables de entorno desde .env si existe y dotenv está disponible
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenv no está disponible, usar solo variables de entorno del sistema
    pass

# Usuario y proyecto (para paths dinámicos)
HDFS_USER = os.getenv("HDFS_USER", "amalia")
HDFS_GROUP = os.getenv("HDFS_GROUP", "amalia")
PROJECT_NAME = os.getenv("PROJECT_NAME", "energy_data")

# Kafka Configuration
# Múltiples brokers para alta disponibilidad (separados por comas)
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "kafka:9092,kafka2:9093,kafka3:9094")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "energy_stream")

# HDFS Configuration
HDFS_NAMENODE = os.getenv("HDFS_NAMENODE", "namenode")
HDFS_PORT = int(os.getenv("HDFS_PORT", "9000"))
HDFS_BASE_PATH = f"/user/{HDFS_USER}/{PROJECT_NAME}"
HDFS_PATH = f"hdfs://{HDFS_NAMENODE}:{HDFS_PORT}{HDFS_BASE_PATH}"

# Hive Configuration
HIVE_METASTORE_URI = os.getenv("HIVE_METASTORE_URI", "thrift://hive-metastore:9083")
HIVE_TABLE_NAME = os.getenv("HIVE_TABLE_NAME", "energy_data")

# Checkpoint Configuration (usar HDFS para que sobreviva a reinicios)
CHECKPOINT_LOCATION = os.getenv(
    "SPARK_CHECKPOINT_LOCATION",
    f"hdfs://{HDFS_NAMENODE}:{HDFS_PORT}{HDFS_BASE_PATH}/_checkpoints"
)
SPARK_PROCESSING_INTERVAL = os.getenv("SPARK_PROCESSING_INTERVAL", "60")
SPARK_APP_NAME = os.getenv("SPARK_APP_NAME", "EnergyDataConsumer")

# Esquema de datos (según el producer)
DATA_SCHEMA = {
    "datetime": "timestamp",
    "global_active_power": "double",
    "global_reactive_power": "double",
    "voltage": "double",
    "global_intensity": "double",
    "sub_metering_1": "double",
    "sub_metering_2": "double",
    "sub_metering_3": "double"
}

