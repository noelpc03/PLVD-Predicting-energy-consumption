# config.py

KAFKA_BROKER = "kafka:9092"
TOPIC = "energy_stream"           # topic donde enviaremos los datos
SEND_INTERVAL = 0.5               # segundos entre cada registro (según requerimiento)
DATASET_PATH = "data/dataset.txt"
MAX_RETRIES = 3  # la cantidad de veces que se reenvia esa vaina si falla