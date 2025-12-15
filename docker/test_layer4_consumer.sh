
#!/bin/bash
# test_layer4_consumer.sh - Prueba el Spark Consumer

echo "=========================================="
echo "🧪 PRUEBA CAPA 4: CONSUMO (SPARK CONSUMER)"
echo "=========================================="
echo ""

# 1. Verificar que Consumer está corriendo
echo "📋 1. Verificando Spark Consumer..."
docker ps | grep spark-consumer
if [ $? -eq 0 ]; then
    echo "✅ Spark Consumer está corriendo"
else
    echo "❌ Spark Consumer NO está corriendo"
    exit 1
fi
echo ""

# 2. Verificar logs del Consumer
echo "📋 2. Verificando logs del Consumer..."
echo "   Estado del consumer:"
docker logs spark-consumer --tail 30 2>&1 | grep -E "Consumer iniciado|Procesando|Leyendo|Transformando|Escribiendo|Error|Exception" | tail -10
echo ""

# 3. Verificar errores críticos
echo "📋 3. Verificando errores en logs..."
ERRORS=$(docker logs spark-consumer 2>&1 | grep -i "error\|exception\|fatal\|failed" | tail -10)
if [ -z "$ERRORS" ]; then
    echo "✅ No se encontraron errores críticos"
else
    echo "⚠️  Errores encontrados:"
    echo "$ERRORS"
fi
echo ""

# 4. Verificar descarga de dependencias
echo "📋 4. Verificando descarga de dependencias..."
if docker logs spark-consumer 2>&1 | grep -q "hadoop-client-api.*jar"; then
    echo "✅ Dependencias descargadas correctamente"
else
    echo "⚠️  Verificando estado de dependencias..."
    docker exec spark-consumer ls -la /root/.ivy2/jars/ | grep -E "kafka|hadoop" | head -5
fi
echo ""

# 5. Verificar conexión Consumer -> Kafka
echo "📋 5. Verificando conectividad Consumer -> Kafka..."
docker exec spark-consumer nc -zv kafka 9092 > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Consumer puede conectarse a Kafka"
else
    echo "❌ Consumer NO puede conectarse a Kafka"
fi
echo ""

# 6. Verificar conexión Consumer -> HDFS
echo "📋 6. Verificando conectividad Consumer -> HDFS..."
docker exec spark-consumer nc -zv namenode 9000 > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Consumer puede conectarse a HDFS"
else
    echo "❌ Consumer NO puede conectarse a HDFS"
fi
echo ""

# 7. Verificar datos en HDFS
echo "📋 7. Verificando datos escritos en HDFS..."
HDFS_PATH="/user/amalia/energy_data/streaming"
docker exec namenode curl -s "http://localhost:9870/webhdfs/v1${HDFS_PATH}?op=LISTSTATUS" 2>&1 | python3 -m json.tool > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Hay datos en HDFS en $HDFS_PATH"
    echo "   Estructura:"
    docker exec namenode curl -s "http://localhost:9870/webhdfs/v1${HDFS_PATH}?op=LISTSTATUS" 2>&1 | python3 -c "
import json, sys
data = json.load(sys.stdin)
if 'FileStatuses' in data:
    for f in data['FileStatuses']['FileStatus'][:5]:
        print(f\"   - {f.get('pathSuffix', 'root')} ({f.get('type', 'UNKNOWN')})\")
" 2>&1
else
    echo "⚠️  No se encontraron datos en HDFS o hay un error de acceso"
fi
echo ""

# 8. Verificar Spark UI
echo "📋 8. Verificando Spark UI..."
docker exec spark-consumer curl -s http://localhost:4040 > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Spark UI está accesible"
else
    echo "⚠️  Spark UI no está accesible (puede estar en otro puerto)"
    docker exec spark-consumer netstat -tlnp 2>/dev/null | grep 404
fi
echo ""

# 9. Verificar procesos Spark
echo "📋 9. Verificando procesos Spark..."
docker exec spark-consumer ps aux | grep -E "spark|java.*SparkSubmit" | grep -v grep | head -3
echo ""

echo "=========================================="
echo "✅ PRUEBA CAPA 4 COMPLETADA"
echo "=========================================="

