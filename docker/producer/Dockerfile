# Dockerfile for Producer - optimizado para tamaño mínimo
FROM python:3.10-slim

# Combinar comandos para reducir capas y limpiar caché
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Copy requirements and install en un solo paso
# Aumentar timeout y retries para conexiones lentas
COPY producer/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir \
    --timeout=10000 \
    --retries=5 \
    -r /tmp/requirements.txt && \
    rm -rf /tmp/requirements.txt && \
    pip cache purge || true

# Create app dir (code will be volume-mounted at runtime)
WORKDIR /app

# Default command is provided by docker-compose
