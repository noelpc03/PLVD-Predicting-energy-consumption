#!/bin/bash
# test_all_layers.sh - Ejecuta todas las pruebas por capas

echo "=========================================="
echo "🧪 EJECUTANDO TODAS LAS PRUEBAS POR CAPAS"
echo "=========================================="
echo ""

LAYERS=(
    "test_layer1_infrastructure.sh:Infraestructura Base"
    "test_layer2_messaging.sh:Mensajería (Kafka)"
    "test_layer3_producer.sh:Producción (Producer)"
    "test_layer4_consumer.sh:Consumo (Spark Consumer)"
    "test_layer5_storage.sh:Almacenamiento (HDFS + Hive)"
    "test_layer6_dashboard.sh:Visualización (Dashboard)"
)

FAILED=0
PASSED=0

for layer in "${LAYERS[@]}"; do
    SCRIPT="${layer%%:*}"
    NAME="${layer##*:}"
    
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "▶️  Ejecutando: $NAME"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    if [ -f "$SCRIPT" ] && [ -x "$SCRIPT" ]; then
        ./$SCRIPT
        RESULT=$?
        if [ $RESULT -eq 0 ]; then
            echo "✅ $NAME: PASÓ"
            ((PASSED++))
        else
            echo "❌ $NAME: FALLÓ (código: $RESULT)"
            ((FAILED++))
        fi
    else
        echo "⚠️  Script $SCRIPT no encontrado o no es ejecutable"
        ((FAILED++))
    fi
    
    sleep 2
done

echo ""
echo "=========================================="
echo "📊 RESUMEN DE PRUEBAS"
echo "=========================================="
echo "✅ Pruebas pasadas: $PASSED"
echo "❌ Pruebas fallidas: $FAILED"
echo "📈 Total: $((PASSED + FAILED))"
echo ""

if [ $FAILED -eq 0 ]; then
    echo "🎉 ¡Todas las pruebas pasaron!"
    exit 0
else
    echo "⚠️  Algunas pruebas fallaron. Revisa los logs arriba."
    exit 1
fi

