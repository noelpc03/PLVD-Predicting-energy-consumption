#!/bin/bash
# Script para inicializar HDFS con los directorios necesarios

# Cargar variables de entorno desde .env si existe
if [ -f "../.env" ]; then
    export $(cat ../.env | grep -v '^#' | xargs)
fi

# Valores por defecto si no están definidos
HDFS_USER=${HDFS_USER:-amalia}
HDFS_GROUP=${HDFS_GROUP:-amalia}
PROJECT_NAME=${PROJECT_NAME:-energy_data}
HDFS_USER_PERMISSIONS=${HDFS_USER_PERMISSIONS:-777}
HDFS_HIVE_PERMISSIONS=${HDFS_HIVE_PERMISSIONS:-755}

echo "🚀 Inicializando HDFS..."
echo "   Usuario: $HDFS_USER"
echo "   Proyecto: $PROJECT_NAME"

# Usar hdfs://mycluster directamente (configuración HA completa)
# Los datanodes ahora tienen la configuración HA necesaria para resolver mycluster
HDFS_URI="hdfs://mycluster"
echo "🔍 Usando hdfs://mycluster (cluster HA)"

# Esperar a que el cluster HA esté accesible
echo "⏳ Esperando a que el cluster HA esté accesible..."
MAX_WAIT=120
WAIT_COUNT=0
CLUSTER_READY=false

while [ $WAIT_COUNT -lt $MAX_WAIT ] && [ "$CLUSTER_READY" = false ]; do
    if docker exec namenode hdfs dfsadmin -fs ${HDFS_URI} -report 2>/dev/null > /dev/null; then
        CLUSTER_READY=true
        echo "✅ Cluster HA accesible vía ${HDFS_URI}"
    else
        echo "⏳ Esperando... ($WAIT_COUNT/$MAX_WAIT segundos)"
        sleep 2
        WAIT_COUNT=$((WAIT_COUNT + 2))
    fi
done

if [ "$CLUSTER_READY" = false ]; then
    echo "⚠️  Timeout esperando al cluster HA. Continuando de todas formas..."
    echo "   Esto puede ser normal si el cluster aún está iniciando."
fi

# Salir del safe mode si está activo (necesario para crear directorios)
echo "🔓 Verificando safe mode..."
SAFE_MODE=$(docker exec namenode hdfs dfsadmin -fs ${HDFS_URI} -safemode get 2>/dev/null | grep -o "ON\|OFF" || echo "UNKNOWN")
if [ "$SAFE_MODE" = "ON" ]; then
    echo "⚠️  Safe mode está activo. Intentando salir..."
    docker exec namenode hdfs dfsadmin -fs ${HDFS_URI} -safemode leave 2>/dev/null || true
    sleep 2
    SAFE_MODE=$(docker exec namenode hdfs dfsadmin -fs ${HDFS_URI} -safemode get 2>/dev/null | grep -o "ON\|OFF" || echo "UNKNOWN")
    if [ "$SAFE_MODE" = "ON" ]; then
        echo "⚠️  No se pudo salir del safe mode. Esto puede ser normal si no hay datanodes conectados."
        echo "   Continuando de todas formas..."
    else
        echo "✅ Safe mode desactivado"
    fi
else
    echo "✅ Safe mode no está activo"
fi

# Verificar datanodes (opcional, no bloqueante)
DATANODE_COUNT=$(docker exec namenode hdfs dfsadmin -fs ${HDFS_URI} -report 2>/dev/null | grep -c "Live datanodes" || echo "0")
if [ "$DATANODE_COUNT" -gt 0 ]; then
    echo "✅ Datanodes conectados: $DATANODE_COUNT"
else
    echo "⚠️  No hay datanodes conectados aún. Esto puede ser normal durante el inicio."
    echo "   Los directorios se crearán de todas formas."
fi

# Crear directorios necesarios con configuración dinámica
USER_PATH="/user/${HDFS_USER}"
PROJECT_PATH="${USER_PATH}/${PROJECT_NAME}"
STREAMING_PATH="${PROJECT_PATH}/streaming"

echo "📁 Creando directorios en HDFS..."

# Crear directorios del proyecto
docker exec namenode bash -c "hdfs dfs -fs ${HDFS_URI} -mkdir -p ${STREAMING_PATH}" 2>&1 | grep -v "already exists" || true
docker exec namenode bash -c "hdfs dfs -fs ${HDFS_URI} -chown -R ${HDFS_USER}:${HDFS_GROUP} ${USER_PATH}" 2>&1 || true
docker exec namenode bash -c "hdfs dfs -fs ${HDFS_URI} -chmod -R ${HDFS_USER_PERMISSIONS} ${USER_PATH}" 2>&1 || true

# Crear directorio para warehouse de Hive
docker exec namenode bash -c "hdfs dfs -fs ${HDFS_URI} -mkdir -p /user/hive/warehouse" 2>&1 | grep -v "already exists" || true
docker exec namenode bash -c "hdfs dfs -fs ${HDFS_URI} -chown -R hive:hive /user/hive" 2>&1 || true
docker exec namenode bash -c "hdfs dfs -fs ${HDFS_URI} -chmod -R ${HDFS_HIVE_PERMISSIONS} /user/hive" 2>&1 || true

echo "✅ Directorios HDFS creados:"
echo "   Verificando directorios del proyecto..."
docker exec namenode bash -c "hdfs dfs -fs ${HDFS_URI} -ls -R ${USER_PATH}" 2>&1 || echo "   ⚠️  No se pudieron listar los directorios (puede ser normal si el namenode aún está iniciando)"
echo "   Verificando directorios de Hive..."
docker exec namenode bash -c "hdfs dfs -fs ${HDFS_URI} -ls -R /user/hive" 2>&1 || echo "   ⚠️  No se pudieron listar los directorios de Hive"

echo "✅ Inicialización completada"

