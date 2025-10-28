FROM apache/spark:3.5.0

# Cambiar a root para evitar problemas de permisos
USER root

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio para la caché de Ivy con permisos adecuados
RUN mkdir -p /tmp/.ivy2/cache && mkdir -p /tmp/.ivy2/jars
RUN chmod -R 777 /tmp/.ivy2

# Mantener como root para evitar problemas de permisos al ejecutar

