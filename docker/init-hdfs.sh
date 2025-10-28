#!/bin/bash
# Script para inicializar HDFS con los directorios necesarios

echo "🚀 Inicializando HDFS..."

# Esperar a que Namenode esté listo
until docker exec namenode hdfs dfsadmin -report 2>/dev/null | grep -q "Live datanodes"; do
    echo "⏳ Esperando a que Namenode esté listo..."
    sleep 2
done

echo "✅ Namenode listo"

# Crear directorios necesarios
docker exec namenode bash -c "hdfs dfs -mkdir -p /user/amalia/energy_data/streaming"
docker exec namenode bash -c "hdfs dfs -chown -R amalia:amalia /user/amalia"
docker exec namenode bash -c "hdfs dfs -chmod -R 755 /user/amalia"

# Crear directorio para warehouse de Hive
docker exec namenode bash -c "hdfs dfs -mkdir -p /user/hive/warehouse"
docker exec namenode bash -c "hdfs dfs -chown -R hive:hive /user/hive"
docker exec namenode bash -c "hdfs dfs -chmod -R 755 /user/hive"

echo "✅ Directorios HDFS creados:"
docker exec namenode bash -c "hdfs dfs -ls -R /user/amalia"
docker exec namenode bash -c "hdfs dfs -ls -R /user/hive"

echo "✅ Inicialización completada"

