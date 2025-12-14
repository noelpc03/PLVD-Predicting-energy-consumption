FROM apache/spark:3.5.0

# Cambiar a root para evitar problemas de permisos
USER root

# Instalar dependencias del sistema y limpiar en un solo paso
RUN apt-get update && apt-get install -y --no-install-recommends \
    netcat-openbsd \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Pre-descargar dependencia de Kafka y crear directorios en un solo paso
# Combinar comandos para reducir capas
RUN echo 'print("Downloading dependencies...")' > /tmp/dummy.py && \
    /opt/spark/bin/spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0 \
    --repositories https://repo1.maven.org/maven2 \
    /tmp/dummy.py 2>&1 | grep -E "(Downloading|downloading|resolving|Ivy)" || true && \
    rm -f /tmp/dummy.py && \
    mkdir -p /tmp/.ivy2/cache /tmp/.ivy2/jars /root/.ivy2/cache /root/.ivy2/jars && \
    chmod -R 777 /tmp/.ivy2 /root/.ivy2

# Mantener como root para evitar problemas de permisos al ejecutar

