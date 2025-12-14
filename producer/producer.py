# producer.py

import time
from config import SEND_INTERVAL, TOPIC
from data_loader import load_data
from message_builder import build_message
from kafka_client import create_producer, send_message

def main():
    # Crear producer
    producer = create_producer()

    # Cargar y limpiar datos
    df = load_data()

    print(f"📤 Inicio de envío de {len(df)} registros cada {SEND_INTERVAL} segundos al topic '{TOPIC}'...")

    for idx, (_, row) in enumerate(df.iterrows(), 1):
        message = build_message(row)
        send_message(producer, message)
        
        if idx % 100 == 0:
            print(f"📊 Procesados {idx}/{len(df)} registros...")

        # Opcional: pausar si se configuró un intervalo
        if SEND_INTERVAL > 0:
            time.sleep(SEND_INTERVAL)

    producer.close()
    print("✅ Todos los mensajes enviados.")

if __name__ == "__main__":
    main()
