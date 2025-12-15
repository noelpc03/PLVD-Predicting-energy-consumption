```bash
#!/bin/bash
# test_layer5_storage.sh - Prueba HDFS y Hive

echo "=========================================="
echo "🧪 PRUEBA CAPA 5: ALMACENAMIENTO (HDFS + HIVE)"
echo "=========================================="
echo ""

# 1. Verificar Hive Metastore
echo "📋 1. Verificando Hive Metastore..."
docker ps | grep hive-metastore
if [ $? -eq 0 ]; then
    echo "✅ Hive Metastore está corriendo"
    docker exec spark-consumer nc -zv hive-metastore 9083 > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo "✅ Puerto 9083 accesible"
    else
        echo "❌ Puerto 9083 NO accesible"
    fi
else
    echo "❌ Hive Metastore NO está corriendo"
fi
echo ""

# 2. Verificar datos Parquet en HDFS
echo "📋 2. Verificando datos Parquet en HDFS..."
HDFS_PATH="/user/amalia/energy_data/streaming"
RESPONSE=$(docker exec namenode curl -s "http://localhost:9870/webhdfs/v1${HDFS_PATH}?op=LISTSTATUS" 2>&1)
if echo "$RESPONSE" | python3 -m json.tool > /dev/null 2>&1; then
    echo "✅ Path de HDFS accesible"
    COUNT=$(echo "$RESPONSE" | python3 -c "
import json, sys
data = json.load(sys.stdin)
if 'FileStatuses' in data:
    print(len(data['FileStatuses']['FileStatus']))
else:
    print(0)
" 2>&1)
    echo "   Archivos/directorios encontrados: $COUNT"
else
    echo "❌ Error accediendo a HDFS"
    echo "   Respuesta: ${RESPONSE:0:200}"
fi
echo ""

# 3. Verificar estructura de particiones
echo "📋 3. Verificando estructura de particiones..."
docker exec namenode curl -s "http://localhost:9870/webhdfs/v1${HDFS_PATH}?op=LISTSTATUS" 2>&1 | python3 -c "
import json, sys
data = json.load(sys.stdin)
if 'FileStatuses' in data:
    partitions = [f['pathSuffix'] for f in data['FileStatuses']['FileStatus'] if f.get('type') == 'DIRECTORY']
    if partitions:
        print('✅ Particiones encontradas:')
        for p in partitions[:5]:
            print(f'   - {p}')
    else:
        print('⚠️  No se encontraron particiones')
" 2>&1
echo ""

# 4. Ejecutar query de prueba con Spark SQL
echo "📋 4. Ejecutando query de prueba (contar registros)..."
QUERY="SELECT COUNT(*) as total FROM parquet.\`hdfs://namenode:9000${HDFS_PATH}\`"
docker exec spark-consumer /opt/spark/bin/spark-submit \
    --master local[1] \
    --driver-memory 512m \
    --executor-memory 512m \
    --conf spark.hadoop.fs.defaultFS=hdfs://namenode:9000 \
    /app/consumer/spark_query.py "$QUERY" "hdfs://namenode:9000" 2>&1 | tail -5
echo ""

# 5. Verificar tabla Hive (si existe)
echo "📋 5. Verificando tabla Hive..."
docker exec spark-consumer /opt/spark/bin/spark-submit \
    --master local[1] \
    --driver-memory 512m \
    --conf spark.hadoop.fs.defaultFS=hdfs://namenode:9000 \
    --conf spark.sql.catalogImplementation=hive \
    --conf hive.metastore.uris=thrift://hive-metastore:9083 \
    -c "
from pyspark.sql import SparkSession
spark = SparkSession.builder.appName('Test').enableHiveSupport().getOrCreate()
try:
    spark.sql('SHOW TABLES').show()
    print('✅ Tablas Hive accesibles')
except Exception as e:
    print(f'⚠️  Error accediendo a Hive: {e}')
spark.stop()
" 2>&1 | tail -5
echo ""

# 6. Verificar formato Parquet
echo "📋 6. Verificando formato Parquet..."
# Intentar leer un archivo Parquet
docker exec spark-consumer /opt/spark/bin/spark-submit \
    --master local[1] \
    --driver-memory 512m \
    --conf spark.hadoop.fs.defaultFS=hdfs://namenode:9000 \
    -c "
from pyspark.sql import SparkSession
spark = SparkSession.builder.appName('Test').getOrCreate()
try:
    df = spark.read.parquet('hdfs://namenode:9000${HDFS_PATH}')
    print(f'✅ Formato Parquet válido')
    print(f'   Columnas: {df.columns}')
    print(f'   Registros: {df.count()}')
except Exception as e:
    print(f'❌ Error leyendo Parquet: {e}')
spark.stop()
" 2>&1 | tail -5
echo ""

echo "=========================================="
echo "✅ PRUEBA CAPA 5 COMPLETADA"
echo "=========================================="
```
