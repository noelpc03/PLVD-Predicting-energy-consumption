```bash
#!/bin/bash
# test_layer6_dashboard.sh - Prueba el Dashboard

echo "=========================================="
echo "🧪 PRUEBA CAPA 6: VISUALIZACIÓN (DASHBOARD)"
echo "=========================================="
echo ""

# 1. Verificar que Dashboard está corriendo
echo "📋 1. Verificando Dashboard..."
docker ps | grep dashboard
if [ $? -eq 0 ]; then
    echo "✅ Dashboard está corriendo"
else
    echo "❌ Dashboard NO está corriendo"
    exit 1
fi
echo ""

# 2. Verificar puerto del Dashboard
echo "📋 2. Verificando puerto del Dashboard..."
PORT=$(docker port dashboard | cut -d: -f2)
if [ ! -z "$PORT" ]; then
    echo "✅ Dashboard escuchando en puerto $PORT"
    curl -s http://localhost:$PORT > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo "✅ Dashboard accesible vía HTTP"
    else
        echo "❌ Dashboard NO accesible vía HTTP"
    fi
else
    echo "❌ No se pudo determinar el puerto"
fi
echo ""

# 3. Probar API de health check
echo "📋 3. Probando API /api/health..."
HEALTH=$(curl -s http://localhost:$PORT/api/health 2>&1)
if echo "$HEALTH" | grep -q "healthy"; then
    echo "✅ Health check exitoso"
    echo "   Respuesta: $HEALTH"
else
    echo "⚠️  Health check falló o respuesta inesperada"
    echo "   Respuesta: $HEALTH"
fi
echo ""

# 4. Probar API /api/latest
echo "📋 4. Probando API /api/latest..."
LATEST=$(curl -s http://localhost:$PORT/api/latest 2>&1)
if echo "$LATEST" | python3 -m json.tool > /dev/null 2>&1; then
    COUNT=$(echo "$LATEST" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('count', 0))" 2>&1)
    if [ "$COUNT" -gt 0 ]; then
        echo "✅ API /api/latest funciona (retornó $COUNT registros)"
    else
        echo "⚠️  API /api/latest funciona pero no hay datos"
    fi
else
    echo "❌ API /api/latest retornó respuesta inválida"
    echo "   Respuesta: ${LATEST:0:200}"
fi
echo ""

# 5. Probar API /api/statistics
echo "📋 5. Probando API /api/statistics..."
STATS=$(curl -s http://localhost:$PORT/api/statistics 2>&1)
if echo "$STATS" | python3 -m json.tool > /dev/null 2>&1; then
    echo "✅ API /api/statistics funciona"
    echo "   Estadísticas:"
    echo "$STATS" | python3 -c "
import json, sys
data = json.load(sys.stdin)
if 'data' in data:
    for k, v in data['data'].items():
        print(f'   - {k}: {v}')
" 2>&1
else
    echo "❌ API /api/statistics retornó respuesta inválida"
fi
echo ""

# 6. Probar API /api/timeseries
echo "📋 6. Probando API /api/timeseries..."
TIMESERIES=$(curl -s http://localhost:$PORT/api/timeseries 2>&1)
if echo "$TIMESERIES" | python3 -m json.tool > /dev/null 2>&1; then
    COUNT=$(echo "$TIMESERIES" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('count', 0))" 2>&1)
    echo "✅ API /api/timeseries funciona (retornó $COUNT puntos)"
else
    echo "❌ API /api/timeseries retornó respuesta inválida"
fi
echo ""

# 7. Verificar logs del Dashboard
echo "📋 7. Verificando logs del Dashboard..."
echo "   Últimas peticiones:"
docker logs dashboard --tail 20 2>&1 | grep "GET\|POST" | tail -5
echo ""

# 8. Verificar errores en logs
echo "📋 8. Verificando errores en logs..."
ERRORS=$(docker logs dashboard 2>&1 | grep -i "error\|exception\|failed" | tail -5)
if [ -z "$ERRORS" ]; then
    echo "✅ No se encontraron errores"
else
    echo "⚠️  Errores encontrados:"
    echo "$ERRORS"
fi
echo ""

# 9. Verificar conectividad Dashboard -> Spark Consumer
echo "📋 9. Verificando conectividad Dashboard -> Spark Consumer..."
docker exec dashboard ping -c 2 spark-consumer > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Dashboard puede comunicarse con Spark Consumer"
else
    echo "❌ Dashboard NO puede comunicarse con Spark Consumer"
fi
echo ""

echo "=========================================="
echo "✅ PRUEBA CAPA 6 COMPLETADA"
echo "=========================================="
echo ""
echo "🌐 Dashboard disponible en: http://localhost:$PORT"
```
