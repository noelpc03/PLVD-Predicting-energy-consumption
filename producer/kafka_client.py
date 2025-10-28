# kafka_client.py

import time
from kafka import KafkaProducer
from kafka.errors import KafkaError
from config import KAFKA_BROKER, TOPIC, MAX_RETRIES

def create_producer():
    return KafkaProducer(
        bootstrap_servers=KAFKA_BROKER,
        value_serializer=lambda v: v.encode('utf-8')
    )

def send_message(producer, message):
    retries = 0
    while retries < MAX_RETRIES:
        try:
            future = producer.send(TOPIC, value=message)
            future.get(timeout=10)  # espera confirmación
            print(f"📤 Enviado: {message}")
            break
        except KafkaError as e:
            print(f"❌ Error enviando mensaje: {e}. Reintentando...")
            retries += 1
            time.sleep(1)
    else:
        print(f"⚠️ No se pudo enviar el mensaje después de {MAX_RETRIES} intentos.")
