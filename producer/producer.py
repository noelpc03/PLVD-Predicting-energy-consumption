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

    failed_messages = 0
    for idx, (_, row) in enumerate(df.iterrows(), 1):
        message = build_message(row)
        success = send_message(producer, message)
        
        if not success:
            failed_messages += 1
        
        if idx % 100 == 0:
            print(f"📊 Procesados {idx}/{len(df)} registros... "
                  f"(fallidos: {failed_messages})")

        # Opcional: pausar si se configuró un intervalo
        if SEND_INTERVAL > 0:
            time.sleep(SEND_INTERVAL)

    producer.close()
    if failed_messages == 0:
        print(f"✅ Todos los {len(df)} mensajes enviados exitosamente.")
    else:
        print(f"⚠️  Proceso completado: {len(df) - failed_messages}/{len(df)} mensajes enviados, "
              f"{failed_messages} fallaron.")

if __name__ == "__main__":
    main()
