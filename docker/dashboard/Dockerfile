FROM python:3.10-slim

# Instalar solo dependencias esenciales (sin compiladores innecesarios)
# Docker CLI es necesario para ejecutar comandos en otros contenedores
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    gnupg \
    lsb-release \
    && rm -rf /var/lib/apt/lists/*

# Instalar Docker CLI (versión mínima necesaria)
RUN curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null \
    && apt-get update \
    && apt-get install -y --no-install-recommends docker-ce-cli \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Crear directorio de trabajo
WORKDIR /app

# Copiar requirements e instalar dependencias
# Aumentar timeout y retries para conexiones lentas
COPY board/requirements.txt .
RUN pip install --no-cache-dir \
    --timeout=10000 \
    --retries=5 \
    -r requirements.txt

# Copiar código de la aplicación
COPY board/ .

# Exponer puerto
EXPOSE 5000

# Comando para ejecutar la aplicación
CMD ["python", "app.py"]

