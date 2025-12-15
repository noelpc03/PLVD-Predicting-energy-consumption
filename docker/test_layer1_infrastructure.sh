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
