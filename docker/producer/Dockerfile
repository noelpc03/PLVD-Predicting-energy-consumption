# Dockerfile for Producer - preinstall Python deps to avoid runtime pip issues
FROM python:3.10-slim

# Install system dependencies if needed (curl/ca-certs already present in slim)
RUN pip install --no-cache-dir --upgrade pip

# Copy requirements and install
COPY producer/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Create app dir (code will be volume-mounted at runtime)
WORKDIR /app

# Default command is provided by docker-compose
