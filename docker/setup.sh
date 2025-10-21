#!/usr/bin/env bash
set -e

# desde la raíz del repo: docker/
docker compose up -d

echo "Esperando a que Namenode esté listo..."
sleep 10

# Copiar dataset dentro del container namenode
if [ -f ../data/dataset.txt ]; then
  docker cp ../data/dataset.txt namenode:/tmp/dataset.txt
  docker exec -it namenode bash -c "hdfs dfs -mkdir -p /user/amalia/data || true; hdfs dfs -put -f /tmp/dataset.txt /user/amalia/data/ || true; hdfs dfs -ls /user/amalia/data"
  echo "Dataset copiado a HDFS en /user/amalia/data/dataset.txt"
else
  echo "No se encontró ../data/dataset.txt — colócalo allí y vuelve a ejecutar."
fi
