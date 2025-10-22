# producer.py

import time
from kafka import KafkaProducer
from config import KAFKA_BROKER, TOPIC, SEND_INTERVAL, DATASET_PATH

def main():
    # Crear el producer
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BROKER,
        value_serializer=lambda v: v.encode('utf-8')  # convertir strings a bytes
    )

    print(f"Conectado a Kafka en {KAFKA_BROKER}, enviando a topic '{TOPIC}'")

    with open(DATASET_PATH, "r") as file:
        # Saltar encabezado
        header = next(file)

        for line in file:
            line = line.strip()
            if not line:
                continue

            # Enviar mensaje a Kafka
            producer.send(TOPIC, value=line)
            print(f"📤 Enviado: {line}")

            # Esperar intervalo definido
            time.sleep(SEND_INTERVAL)

    # Cerrar el producer
    producer.close()
    print("✅ Todos los mensajes enviados.")

if __name__ == "__main__":
    main()
