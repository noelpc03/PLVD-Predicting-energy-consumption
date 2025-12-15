# kafka_client.py

import time
from kafka import KafkaProducer
from kafka.errors import KafkaError, KafkaTimeoutError, KafkaConnectionError
from config import KAFKA_BROKER, TOPIC, MAX_RETRIES

def _validate_kafka_broker(broker_string):
    """
    Valida el formato del string de brokers de Kafka
    
    Args:
        broker_string: String con brokers separados por comas (ej: "broker1:9092,broker2:9093")
    
    Returns:
        Lista de brokers validados
    """
    if not broker_string or not broker_string.strip():
        raise ValueError(
            "❌ Error: KAFKA_BROKER está vacío o no está configurado.\n"
            "   Por favor, configura la variable de entorno KAFKA_BROKER con el formato:\n"
            "   'broker1:9092,broker2:9093' o 'broker:9092'"
        )
    
    # Separar brokers por comas y limpiar espacios
    brokers = [b.strip() for b in broker_string.split(',') if b.strip()]
    
    if not brokers:
        raise ValueError(
            f"❌ Error: No se encontraron brokers válidos en KAFKA_BROKER.\n"
            f"   Valor recibido: '{broker_string}'\n"
            f"   Formato esperado: 'broker1:9092,broker2:9093'"
        )
    
    # Validar formato básico (debe tener ':' para separar host:puerto)
    for broker in brokers:
        if ':' not in broker:
            raise ValueError(
                f"❌ Error: Formato de broker inválido: '{broker}'\n"
                f"   Formato esperado: 'host:puerto' (ej: 'kafka:9092')"
            )
    
    return brokers

def create_producer():
    """
    Crea un KafkaProducer con validación y manejo de errores mejorado
    
    Returns:
        KafkaProducer configurado
        
    Raises:
        ValueError: Si la configuración de brokers es inválida
        KafkaConnectionError: Si no se puede conectar a Kafka
        Exception: Para otros errores de conexión
    """
    try:
        # Validar formato de brokers
        brokers = _validate_kafka_broker(KAFKA_BROKER)
        
        print(f"🔌 Conectando a Kafka brokers: {', '.join(brokers)}")
        
        # Crear producer con configuración mejorada
        producer = KafkaProducer(
            bootstrap_servers=brokers,  # Puede ser lista o string
            value_serializer=lambda v: v.encode('utf-8'),
            # Configuraciones adicionales para mejor manejo de errores
            request_timeout_ms=30000,  # 30 segundos timeout
            retries=3,  # Reintentos automáticos
            acks='all',  # Esperar confirmación de todos los replicas
            max_block_ms=60000  # Tiempo máximo para bloquear si el buffer está lleno
        )
        
        # Intentar una conexión de prueba (opcional pero útil)
        # Nota: KafkaProducer es lazy, así que la conexión real ocurre al enviar el primer mensaje
        print(f"✅ KafkaProducer creado exitosamente")
        
        return producer
        
    except ValueError as e:
        # Error de validación de configuración
        raise
    except (KafkaConnectionError, KafkaTimeoutError) as e:
        error_msg = (
            f"❌ Error de conexión con Kafka:\n"
            f"   Brokers intentados: {', '.join(brokers) if 'brokers' in locals() else KAFKA_BROKER}\n"
            f"   Error: {str(e)}\n"
            f"   Verifica que:\n"
            f"   - Los brokers de Kafka estén corriendo\n"
            f"   - Los nombres de host y puertos sean correctos\n"
            f"   - La red Docker esté configurada correctamente\n"
            f"   - No haya firewalls bloqueando la conexión"
        )
        raise KafkaConnectionError(error_msg) from e
    except Exception as e:
        error_msg = (
            f"❌ Error inesperado al crear KafkaProducer:\n"
            f"   Tipo de error: {type(e).__name__}\n"
            f"   Mensaje: {str(e)}\n"
            f"   Brokers configurados: {KAFKA_BROKER}"
        )
        raise Exception(error_msg) from e

def send_message(producer, message):
    """
    Envía un mensaje a Kafka con manejo de errores mejorado
    
    Args:
        producer: Instancia de KafkaProducer
        message: Mensaje a enviar (string)
    
    Returns:
        bool: True si el mensaje se envió exitosamente, False en caso contrario
    """
    retries = 0
    last_error = None
    
    while retries < MAX_RETRIES:
        try:
            future = producer.send(TOPIC, value=message)
            # Esperar confirmación con timeout
            record_metadata = future.get(timeout=10)
            
            # Mensaje de éxito con información del offset
            print(f"📤 Enviado exitosamente al topic '{TOPIC}' "
                  f"(partition: {record_metadata.partition}, "
                  f"offset: {record_metadata.offset})")
            return True
            
        except KafkaTimeoutError as e:
            last_error = e
            retries += 1
            error_msg = (
                f"⏱️  Timeout enviando mensaje (intento {retries}/{MAX_RETRIES}):\n"
                f"   Topic: {TOPIC}\n"
                f"   Error: {str(e)}\n"
                f"   Posibles causas: Kafka no responde, red lenta, o brokers no disponibles"
            )
            print(error_msg)
            if retries < MAX_RETRIES:
                wait_time = retries * 2  # Backoff exponencial
                print(f"   Esperando {wait_time} segundos antes de reintentar...")
                time.sleep(wait_time)
                
        except KafkaConnectionError as e:
            last_error = e
            retries += 1
            error_msg = (
                f"🔌 Error de conexión con Kafka (intento {retries}/{MAX_RETRIES}):\n"
                f"   Topic: {TOPIC}\n"
                f"   Error: {str(e)}\n"
                f"   Verifica que los brokers de Kafka estén disponibles"
            )
            print(error_msg)
            if retries < MAX_RETRIES:
                wait_time = retries * 2
                print(f"   Esperando {wait_time} segundos antes de reintentar...")
                time.sleep(wait_time)
                
        except KafkaError as e:
            last_error = e
            retries += 1
            error_msg = (
                f"❌ Error de Kafka (intento {retries}/{MAX_RETRIES}):\n"
                f"   Tipo: {type(e).__name__}\n"
                f"   Topic: {TOPIC}\n"
                f"   Error: {str(e)}"
            )
            print(error_msg)
            if retries < MAX_RETRIES:
                wait_time = retries * 2
                print(f"   Esperando {wait_time} segundos antes de reintentar...")
                time.sleep(wait_time)
                
        except Exception as e:
            last_error = e
            retries += 1
            error_msg = (
                f"❌ Error inesperado (intento {retries}/{MAX_RETRIES}):\n"
                f"   Tipo: {type(e).__name__}\n"
                f"   Error: {str(e)}"
            )
            print(error_msg)
            if retries < MAX_RETRIES:
                wait_time = retries * 2
                print(f"   Esperando {wait_time} segundos antes de reintentar...")
                time.sleep(wait_time)
    
    # Si llegamos aquí, todos los reintentos fallaron
    final_error_msg = (
        f"⚠️  No se pudo enviar el mensaje después de {MAX_RETRIES} intentos.\n"
        f"   Topic: {TOPIC}\n"
        f"   Último error: {type(last_error).__name__ if last_error else 'Desconocido'}: {str(last_error) if last_error else 'N/A'}\n"
        f"   Mensaje que falló: {message[:100]}..." if len(message) > 100 else f"   Mensaje que falló: {message}"
    )
    print(final_error_msg)
    return False
