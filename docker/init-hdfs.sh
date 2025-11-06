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

# Esperar a que Namenode esté listo
until docker exec namenode hdfs dfsadmin -report 2>/dev/null | grep -q "Live datanodes"; do
    echo "⏳ Esperando a que Namenode esté listo..."
    sleep 2
done

echo "✅ Namenode listo"

# Crear directorios necesarios con configuración dinámica
USER_PATH="/user/${HDFS_USER}"
PROJECT_PATH="${USER_PATH}/${PROJECT_NAME}"
STREAMING_PATH="${PROJECT_PATH}/streaming"

docker exec namenode bash -c "hdfs dfs -mkdir -p ${STREAMING_PATH}"
docker exec namenode bash -c "hdfs dfs -chown -R ${HDFS_USER}:${HDFS_GROUP} ${USER_PATH}"
docker exec namenode bash -c "hdfs dfs -chmod -R ${HDFS_USER_PERMISSIONS} ${USER_PATH}"

# Crear directorio para warehouse de Hive
docker exec namenode bash -c "hdfs dfs -mkdir -p /user/hive/warehouse"
docker exec namenode bash -c "hdfs dfs -chown -R hive:hive /user/hive"
docker exec namenode bash -c "hdfs dfs -chmod -R ${HDFS_HIVE_PERMISSIONS} /user/hive"

echo "✅ Directorios HDFS creados:"
docker exec namenode bash -c "hdfs dfs -ls -R ${USER_PATH}"
docker exec namenode bash -c "hdfs dfs -ls -R /user/hive"

echo "✅ Inicialización completada"

