#!/bin/bash
# test_layer2_messaging.sh - Prueba Kafka y ZooKeeper

echo "=========================================="
echo "🧪 PRUEBA CAPA 2: MENSAJERÍA (KAFKA)"
echo "=========================================="
echo ""

# 1. Verificar que Kafka brokers están corriendo
echo "📋 1. Verificando Kafka brokers..."
for i in "" "2" "3"; do
    BROKER="kafka$i"
    docker ps | grep $BROKER
    if [ $? -eq 0 ]; then
        HEALTH=$(docker inspect --format='{{.State.Health.Status}}' $BROKER 2>/dev/null)
        echo "✅ $BROKER está corriendo (health: $HEALTH)"
    else
        echo "❌ $BROKER NO está corriendo"
    fi
done
echo ""

# 2. Verificar conectividad con ZooKeeper
echo "📋 2. Verificando conexión Kafka -> ZooKeeper..."
docker exec kafka kafka-broker-api-versions --bootstrap-server localhost:9092 > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Kafka broker 1 responde correctamente"
else
    echo "❌ Kafka broker 1 NO responde"
fi
echo ""

# 3. Crear topic de prueba
echo "📋 3. Creando topic de prueba 'test-topic'..."
docker exec kafka kafka-topics --create \
    --bootstrap-server localhost:9092 \
    --topic test-topic \
    --partitions 3 \
    --replication-factor 3 \
    --if-not-exists 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Topic 'test-topic' creado exitosamente"
else
    echo "⚠️  Topic puede que ya exista o hubo un error"
fi

# Esperar a que las réplicas se sincronicen
echo "⏳ Esperando sincronización de réplicas (5 segundos)..."
sleep 5
echo ""

# 4. Listar topics
echo "📋 4. Listando topics existentes..."
docker exec kafka kafka-topics --list --bootstrap-server localhost:9092
echo ""

# 5. Verificar estado del topic antes de enviar
echo "📋 5. Verificando estado del topic 'test-topic'..."
docker exec kafka kafka-topics --describe \
    --bootstrap-server localhost:9092 \
    --topic test-topic 2>&1 | head -3
echo ""

# 6. Enviar mensaje de prueba
TEST_MESSAGE="test-message-$(date +%s)"
echo "📋 6. Enviando mensaje de prueba: '$TEST_MESSAGE'..."
echo "$TEST_MESSAGE" | docker exec -i kafka kafka-console-producer \
    --bootstrap-server localhost:9092 \
    --topic test-topic > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Mensaje enviado correctamente"
    # Esperar a que el mensaje se propague
    echo "⏳ Esperando propagación del mensaje (3 segundos)..."
    sleep 3
else
    echo "❌ Error al enviar mensaje"
fi
echo ""

# 7. Consumir mensaje de prueba
echo "📋 7. Consumiendo mensaje de prueba..."

# Función para ejecutar con timeout (compatible con macOS y Linux)
run_with_timeout() {
    local timeout_sec=$1
    shift
    if command -v timeout >/dev/null 2>&1; then
        # Linux: usar timeout nativo
        timeout $timeout_sec "$@"
    elif command -v gtimeout >/dev/null 2>&1; then
        # macOS con GNU coreutils instalado
        gtimeout $timeout_sec "$@"
    else
        # macOS sin timeout: usar perl como alternativa
        perl -e 'alarm shift; exec @ARGV' $timeout_sec "$@"
    fi
}

CONSUMED=$(run_with_timeout 10 docker exec kafka kafka-console-consumer \
    --bootstrap-server localhost:9092 \
    --topic test-topic \
    --from-beginning \
    --max-messages 1 \
    --timeout-ms 8000 2>&1)

if echo "$CONSUMED" | grep -q "test-message"; then
    echo "✅ Mensaje recibido correctamente"
    echo "   Mensaje recibido: $(echo "$CONSUMED" | grep "test-message")"
else
    echo "⚠️  No se recibió mensaje"
    echo "   Salida del consumer: $CONSUMED"
fi
echo ""

# 8. Verificar logs de Kafka
echo "📋 8. Verificando logs de Kafka (últimos errores)..."
docker logs kafka 2>&1 | grep -i "error\|exception\|fatal" | tail -5
echo ""

echo "=========================================="
echo "✅ PRUEBA CAPA 2 COMPLETADA"
echo "=========================================="
