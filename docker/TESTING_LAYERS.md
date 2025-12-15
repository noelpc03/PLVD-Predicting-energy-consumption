# 🧪 Plan de Pruebas por Capas

Este documento describe las pruebas incrementales por capa para verificar que cada componente funciona correctamente antes de pasar a la siguiente capa.

## 📊 Arquitectura en Capas

```
┌─────────────────────────────────────────────────────────┐
│ CAPA 6: VISUALIZACIÓN                                   │
│   └─ Dashboard (Flask) → Lee de HDFS                   │
└─────────────────┬───────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────┐
│ CAPA 5: ALMACENAMIENTO                                  │
│   └─ HDFS (Parquet) + Hive Metastore                   │
└─────────────────┬───────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────┐
│ CAPA 4: CONSUMO                                         │
│   └─ Spark Consumer → Lee de Kafka, escribe a HDFS      │
└─────────────────┬───────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────┐
│ CAPA 3: PRODUCCIÓN                                      │
│   └─ Producer (Python) → Envía a Kafka                 │
└─────────────────┬───────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────┐
│ CAPA 2: MENSAJERÍA                                      │
│   └─ Kafka (3 brokers) + ZooKeeper                     │
└─────────────────┬───────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────┐
│ CAPA 1: INFRAESTRUCTURA BASE                            │
│   └─ ZooKeeper, HDFS (NameNode, DataNodes, JournalNodes)│
└─────────────────────────────────────────────────────────┘
```

---

## 🧪 CAPA 1: Infraestructura Base

### Componentes a probar:
- ZooKeeper
- HDFS NameNode (activo y standby)
- HDFS DataNodes (3 nodos)
- JournalNodes (3 nodos)

### Script de Prueba: `test_layer1_infrastructure.sh`

```bash
#!/bin/bash
# test_layer1_infrastructure.sh - Prueba la infraestructura base

echo "=========================================="
echo "🧪 PRUEBA CAPA 1: INFRAESTRUCTURA BASE"
echo "=========================================="
echo ""

# 1. Verificar ZooKeeper
echo "📋 1. Verificando ZooKeeper..."
docker ps | grep zookeeper
if [ $? -eq 0 ]; then
    echo "✅ ZooKeeper está corriendo"
    docker exec zookeeper nc -zv localhost 2181
    echo "✅ Puerto 2181 accesible"
else
    echo "❌ ZooKeeper NO está corriendo"
    exit 1
fi
echo ""

# 2. Verificar NameNode activo
echo "📋 2. Verificando NameNode activo..."
docker ps | grep namenode
if [ $? -eq 0 ]; then
    echo "✅ NameNode está corriendo"
    HEALTH=$(docker inspect --format='{{.State.Health.Status}}' namenode 2>/dev/null)
    echo "   Estado de salud: $HEALTH"
    curl -s http://localhost:9870 | grep -q "HDFS" && echo "✅ Web UI accesible" || echo "⚠️  Web UI no accesible"
else
    echo "❌ NameNode NO está corriendo"
    exit 1
fi
echo ""

# 3. Verificar NameNode standby
echo "📋 3. Verificando NameNode standby..."
docker ps | grep namenode-standby
if [ $? -eq 0 ]; then
    echo "✅ NameNode standby está corriendo"
    HEALTH=$(docker inspect --format='{{.State.Health.Status}}' namenode-standby 2>/dev/null)
    echo "   Estado de salud: $HEALTH"
else
    echo "❌ NameNode standby NO está corriendo"
    exit 1
fi
echo ""

# 4. Verificar DataNodes
echo "📋 4. Verificando DataNodes..."
for i in 1 2 3; do
    if [ $i -eq 1 ]; then
        NODE="datanode"
    else
        NODE="datanode$i"
    fi
    docker ps | grep $NODE
    if [ $? -eq 0 ]; then
        echo "✅ $NODE está corriendo"
        HEALTH=$(docker inspect --format='{{.State.Health.Status}}' $NODE 2>/dev/null)
        echo "   Estado de salud: $HEALTH"
    else
        echo "❌ $NODE NO está corriendo"
    fi
done
echo ""

# 5. Verificar JournalNodes
echo "📋 5. Verificando JournalNodes..."
for i in 1 2 3; do
    NODE="journalnode$i"
    docker ps | grep $NODE
    if [ $? -eq 0 ]; then
        echo "✅ $NODE está corriendo"
    else
        echo "❌ $NODE NO está corriendo"
    fi
done
echo ""

# 6. Verificar conectividad entre servicios
echo "📋 6. Verificando conectividad de red..."
docker exec namenode ping -c 2 datanode > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ NameNode puede comunicarse con DataNode"
else
    echo "❌ Problema de conectividad NameNode -> DataNode"
fi

docker exec namenode ping -c 2 journalnode1 > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ NameNode puede comunicarse con JournalNode"
else
    echo "❌ Problema de conectividad NameNode -> JournalNode"
fi
echo ""

# 7. Verificar logs de errores críticos
echo "📋 7. Verificando logs de errores..."
echo "   NameNode:"
docker logs namenode 2>&1 | grep -i "error\|exception\|fatal" | tail -5
echo "   DataNode:"
docker logs datanode 2>&1 | grep -i "error\|exception\|fatal" | tail -5
echo ""

echo "=========================================="
echo "✅ PRUEBA CAPA 1 COMPLETADA"
echo "=========================================="
```

### Comandos para ejecutar:
```bash
cd docker
chmod +x test_layer1_infrastructure.sh
./test_layer1_infrastructure.sh
```

---

## 🧪 CAPA 2: Mensajería (Kafka)

### Componentes a probar:
- Kafka Broker 1, 2, 3
- Creación de topics
- Producción y consumo de mensajes de prueba

### Script de Prueba: `test_layer2_messaging.sh`

```bash
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
echo ""

# 4. Listar topics
echo "📋 4. Listando topics existentes..."
docker exec kafka kafka-topics --list --bootstrap-server localhost:9092
echo ""

# 5. Enviar mensaje de prueba
echo "📋 5. Enviando mensaje de prueba..."
echo "test-message-$(date +%s)" | docker exec -i kafka kafka-console-producer \
    --bootstrap-server localhost:9092 \
    --topic test-topic > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Mensaje enviado correctamente"
else
    echo "❌ Error al enviar mensaje"
fi
echo ""

# 6. Consumir mensaje de prueba
echo "📋 6. Consumiendo mensaje de prueba..."
timeout 5 docker exec kafka kafka-console-consumer \
    --bootstrap-server localhost:9092 \
    --topic test-topic \
    --from-beginning \
    --max-messages 1 2>&1 | grep -q "test-message" && echo "✅ Mensaje recibido correctamente" || echo "⚠️  No se recibió mensaje"
echo ""

# 7. Verificar logs de Kafka
echo "📋 7. Verificando logs de Kafka (últimos errores)..."
docker logs kafka 2>&1 | grep -i "error\|exception\|fatal" | tail -5
echo ""

echo "=========================================="
echo "✅ PRUEBA CAPA 2 COMPLETADA"
echo "=========================================="
```

### Comandos para ejecutar:
```bash
cd docker
chmod +x test_layer2_messaging.sh
./test_layer2_messaging.sh
```

---

## 🧪 CAPA 3: Producción (Producer)

### Componentes a probar:
- Producer Python
- Conexión a Kafka
- Envío de mensajes al topic correcto
- Formato de mensajes JSON

### Script de Prueba: `test_layer3_producer.sh`

```bash
#!/bin/bash
# test_layer3_producer.sh - Prueba el Producer

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
COUNT=$(timeout 3 docker exec kafka kafka-console-consumer \
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
SAMPLE=$(timeout 3 docker exec kafka kafka-console-consumer \
    --bootstrap-server localhost:9092 \
    --topic energy_stream \
    --from-beginning \
    --max-messages 1 2>&1 | tail -1)
if echo "$SAMPLE" | python3 -m json.tool > /dev/null 2>&1; then
    echo "✅ Formato JSON válido"
    echo "   Muestra: ${SAMPLE:0:100}..."
else
    echo "❌ Formato JSON inválido"
    echo "   Muestra: $SAMPLE"
fi
echo ""

# 7. Verificar estructura del mensaje
echo "📋 7. Verificando estructura del mensaje..."
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
echo ""

echo "=========================================="
echo "✅ PRUEBA CAPA 3 COMPLETADA"
echo "=========================================="
```

### Comandos para ejecutar:
```bash
cd docker
chmod +x test_layer3_producer.sh
./test_layer3_producer.sh
```

---

## 🧪 CAPA 4: Consumo (Spark Consumer)

### Componentes a probar:
- Spark Consumer
- Conexión a Kafka
- Lectura de mensajes
- Escritura a HDFS
- Transformación de datos

### Script de Prueba: `test_layer4_consumer.sh`

```bash
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
```

### Comandos para ejecutar:
```bash
cd docker
chmod +x test_layer4_consumer.sh
./test_layer4_consumer.sh
```

---

## 🧪 CAPA 5: Almacenamiento (HDFS + Hive)

### Componentes a probar:
- Datos en HDFS (formato Parquet)
- Hive Metastore
- Consultas SQL sobre datos

### Script de Prueba: `test_layer5_storage.sh`

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

### Comandos para ejecutar:
```bash
cd docker
chmod +x test_layer5_storage.sh
./test_layer5_storage.sh
```

---

## 🧪 CAPA 6: Visualización (Dashboard)

### Componentes a probar:
- Dashboard Flask
- APIs REST
- Lectura de datos desde HDFS
- Visualización en navegador

### Script de Prueba: `test_layer6_dashboard.sh`

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

### Comandos para ejecutar:
```bash
cd docker
chmod +x test_layer6_dashboard.sh
./test_layer6_dashboard.sh
```

---

## 🚀 Script Maestro: Ejecutar Todas las Pruebas

### Script: `test_all_layers.sh`

```bash
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
```

---

## 📝 Uso

### Ejecutar pruebas individuales:
```bash
cd docker
chmod +x test_layer*.sh
./test_layer1_infrastructure.sh
./test_layer2_messaging.sh
# etc...
```

### Ejecutar todas las pruebas:
```bash
cd docker
chmod +x test_all_layers.sh
./test_all_layers.sh
```

### Ejecutar pruebas en orden incremental:
```bash
cd docker
# Primero levantar solo la capa 1
docker compose up -d zookeeper namenode namenode-standby datanode datanode2 datanode3 journalnode1 journalnode2 journalnode3
./test_layer1_infrastructure.sh

# Luego agregar capa 2
docker compose up -d kafka kafka2 kafka3
./test_layer2_messaging.sh

# Y así sucesivamente...
```

---

## 🔍 Logs Detallados

Para obtener logs más detallados de cada componente:

```bash
# Logs en tiempo real
docker logs -f <container-name>

# Logs con filtros
docker logs <container-name> 2>&1 | grep -i "error\|exception\|warn"

# Últimas N líneas
docker logs <container-name> --tail 100
```

---

## 📋 Checklist de Verificación

- [ ] Capa 1: Infraestructura base funcionando
- [ ] Capa 2: Kafka y ZooKeeper funcionando
- [ ] Capa 3: Producer enviando datos
- [ ] Capa 4: Consumer procesando datos
- [ ] Capa 5: Datos almacenados en HDFS
- [ ] Capa 6: Dashboard mostrando datos

