# config.py
import os

# Intentar cargar variables de entorno desde .env si existe y dotenv está disponible
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenv no está disponible, usar solo variables de entorno del sistema
    pass

# Kafka Configuration
# Múltiples brokers para alta disponibilidad (separados por comas)
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "kafka:9092,kafka2:9093,kafka3:9094")
TOPIC = os.getenv("KAFKA_TOPIC", "energy_stream")

# Producer Configuration
# Default: 0 (envío lo más rápido posible); se puede ralentizar con env
SEND_INTERVAL = float(os.getenv("PRODUCER_SEND_INTERVAL", "0"))  # segundos entre cada registro
DATASET_PATH = os.getenv("PRODUCER_DATASET_PATH", "data/dataset.txt")
MAX_RETRIES = int(os.getenv("PRODUCER_MAX_RETRIES", "3"))  # cantidad de reintentos si falla