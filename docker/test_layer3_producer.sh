#!/bin/bash
# test_layer3_producer.sh - Prueba el Producer

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

echo "=========================================="
echo "🧪 PRUEBA CAPA 3: PRODUCCIÓN (PRODUCER)"
echo "=========================================="
echo ""

# 1. Verificar que Producer está corriendo
echo "📋 1. Verificando Producer..."
docker ps | grep producer
if [ $? -eq 0 ]; then
    echo "✅ Producer está corriendo"
else
    echo "❌ Producer NO está corriendo"
    exit 1
fi
echo ""

# 2. Verificar logs del Producer (últimos 20 líneas)
echo "📋 2. Verificando logs del Producer..."
echo "   Últimos mensajes enviados:"
docker logs producer --tail 20 2>&1 | grep "📤 Enviado:" | tail -5
if [ $? -eq 0 ]; then
    echo "✅ Producer está enviando mensajes"
else
    echo "⚠️  No se encontraron mensajes enviados en los logs"
fi
echo ""

# 3. Verificar errores en logs
echo "📋 3. Verificando errores en logs del Producer..."
ERRORS=$(docker logs producer 2>&1 | grep -i "error\|exception\|failed" | tail -5)
if [ -z "$ERRORS" ]; then
    echo "✅ No se encontraron errores"
else
    echo "⚠️  Errores encontrados:"
    echo "$ERRORS"
fi
echo ""

# 4. Verificar que el Producer puede conectarse a Kafka
echo "📋 4. Verificando conectividad Producer -> Kafka..."
docker exec producer python3 -c "
import socket
import sys
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('kafka', 9092))
    sock.close()
    if result == 0:
        print('✅ Producer puede conectarse a Kafka:9092')
        sys.exit(0)
    else:
        print('❌ Producer NO puede conectarse a Kafka:9092')
        sys.exit(1)
except Exception as e:
    print(f'❌ Error de conexión: {e}')
    sys.exit(1)
"
echo ""

# 5. Verificar que hay mensajes en el topic
echo "📋 5. Verificando mensajes en topic 'energy_stream'..."
COUNT=$(run_with_timeout 3 docker exec kafka kafka-console-consumer \
    --bootstrap-server localhost:9092 \
    --topic energy_stream \
    --from-beginning \
    --max-messages 10 2>&1 | wc -l)
if [ $COUNT -gt 0 ]; then
    echo "✅ Hay mensajes en el topic (al menos $COUNT mensajes)"
else
    echo "⚠️  No se encontraron mensajes en el topic"
fi
echo ""

# 6. Verificar formato JSON de un mensaje
echo "📋 6. Verificando formato JSON de mensajes..."
SAMPLE=$(run_with_timeout 5 docker exec kafka kafka-console-consumer \
    --bootstrap-server localhost:9092 \
    --topic energy_stream \
    --from-beginning \
    --max-messages 1 \
    --timeout-ms 4000 2>&1 | grep -E '^\{' | head -1)

if [ -z "$SAMPLE" ]; then
    echo "⚠️  No se pudo obtener un mensaje del topic"
    echo "   Intentando método alternativo..."
    # Método alternativo: leer directamente sin filtros y buscar JSON
    SAMPLE=$(run_with_timeout 5 docker exec kafka kafka-console-consumer \
        --bootstrap-server localhost:9092 \
        --topic energy_stream \
        --from-beginning \
        --max-messages 1 \
        --timeout-ms 4000 2>/dev/null | grep -E '^\{' | head -1)
fi

if [ -z "$SAMPLE" ]; then
    echo "❌ No se pudo obtener un mensaje para validar"
elif echo "$SAMPLE" | python3 -m json.tool > /dev/null 2>&1; then
    echo "✅ Formato JSON válido"
    echo "   Muestra: ${SAMPLE:0:100}..."
else
    echo "❌ Formato JSON inválido"
    echo "   Muestra: $SAMPLE"
fi
echo ""

# 7. Verificar estructura del mensaje
echo "📋 7. Verificando estructura del mensaje..."
if [ -z "$SAMPLE" ]; then
    echo "⚠️  No se puede validar la estructura: no hay mensaje disponible"
else
    if echo "$SAMPLE" | python3 -c "
import json
import sys
try:
    data = json.load(sys.stdin)
    required = ['datetime', 'global_active_power', 'voltage']
    missing = [f for f in required if f not in data]
    if missing:
        print(f'❌ Campos faltantes: {missing}')
        sys.exit(1)
    else:
        print('✅ Estructura del mensaje correcta')
        print(f'   Campos: {list(data.keys())}')
        sys.exit(0)
except Exception as e:
    print(f'❌ Error parseando JSON: {e}')
    sys.exit(1)
" 2>&1; then
        echo ""
    else
        echo "⚠️  Problema con la estructura del mensaje"
    fi
fi
echo ""

echo "=========================================="
echo "✅ PRUEBA CAPA 3 COMPLETADA"
echo "=========================================="

