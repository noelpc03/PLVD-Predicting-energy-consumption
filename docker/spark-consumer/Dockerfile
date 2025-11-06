FROM apache/spark:3.5.0

# Cambiar a root para evitar problemas de permisos
USER root

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    netcat-openbsd \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Pre-descargar dependencia de Kafka para evitar problemas de red en runtime
# Solo necesitamos spark-sql-kafka ya que no usamos AWS/S3
# Usar un script dummy para forzar la descarga
RUN echo 'print("Downloading dependencies...")' > /tmp/dummy.py && \
    /opt/spark/bin/spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0 \
    --repositories https://repo1.maven.org/maven2 \
    /tmp/dummy.py 2>&1 | grep -E "(Downloading|downloading|resolving|Ivy)" || true

# Crear directorio para la caché de Ivy con permisos adecuados
RUN mkdir -p /tmp/.ivy2/cache && mkdir -p /tmp/.ivy2/jars
RUN mkdir -p /root/.ivy2/cache && mkdir -p /root/.ivy2/jars
RUN chmod -R 777 /tmp/.ivy2
RUN chmod -R 777 /root/.ivy2

# Mantener como root para evitar problemas de permisos al ejecutar

