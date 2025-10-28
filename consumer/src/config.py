# config.py - Configuración del Consumer

# Kafka Configuration
KAFKA_BROKER = "kafka:9092"
KAFKA_TOPIC = "energy_stream"

# HDFS Configuration
HDFS_NAMENODE = "namenode"
HDFS_PORT = 9000
HDFS_PATH = f"hdfs://{HDFS_NAMENODE}:{HDFS_PORT}/user/amalia/energy_data"

# Hive Configuration
HIVE_METASTORE_URI = "thrift://hive-metastore:9083"

# Checkpoint Configuration
CHECKPOINT_LOCATION = "/tmp/spark-checkpoints"

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

