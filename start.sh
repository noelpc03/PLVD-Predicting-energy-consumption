#!/bin/bash
# Script de inicio rápido para el proyecto PLVD

set -e  # Salir si hay algún error

echo "=========================================="
echo "🚀 PLVD - Inicio Rápido"
echo "=========================================="
echo ""

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Función para imprimir con color
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "ℹ️  $1"
}

# ==== VERIFICACIONES PREVIAS ====
echo "📋 Verificando requisitos previos..."
echo ""

# Verificar Docker
if ! command -v docker &> /dev/null; then
    print_error "Docker no está instalado"
    echo "Por favor instala Docker siguiendo INSTALLATION_GUIDE.md"
    exit 1
fi
print_success "Docker instalado: $(docker --version)"

# Verificar Docker Compose
if ! command -v docker compose &> /dev/null; then
    print_error "Docker Compose no está instalado"
    echo "Por favor instala Docker Compose siguiendo INSTALLATION_GUIDE.md"
    exit 1
fi
print_success "Docker Compose instalado"

# Verificar que Docker está corriendo
if ! docker ps &> /dev/null; then
    print_error "Docker no está corriendo"
    echo "Por favor inicia Docker y vuelve a ejecutar este script"
    exit 1
fi
print_success "Docker está corriendo"

# Verificar dataset
if [ ! -f "data/dataset.txt" ]; then
    print_error "Dataset no encontrado en data/dataset.txt"
    echo "Verificando si existe household_power_consumption.txt..."
    if [ -f "household_power_consumption.txt" ]; then
        print_info "Creando carpeta data/ y copiando dataset..."
        mkdir -p data
        cp household_power_consumption.txt data/dataset.txt
        print_success "Dataset copiado a data/dataset.txt"
    else
        print_error "No se encontró el dataset"
        echo "Por favor descarga el dataset y colócalo en data/dataset.txt"
        exit 1
    fi
else
    print_success "Dataset encontrado"
fi

echo ""
echo "=========================================="
echo "🔧 Preparando el entorno..."
echo "=========================================="
echo ""

# Ir al directorio docker
cd docker

# Detener contenedores previos si existen
print_info "Deteniendo contenedores previos (si existen)..."
docker compose down &> /dev/null || true

# Construir imágenes
print_info "Construyendo imágenes Docker (esto puede tomar 5-10 minutos la primera vez)..."
docker compose build

print_success "Imágenes construidas correctamente"

echo ""
echo "=========================================="
echo "🚀 Iniciando servicios..."
echo "=========================================="
echo ""

# Fase 1: Servicios base
print_info "Fase 1: Iniciando Zookeeper, Kafka, HDFS..."
docker compose up -d zookeeper kafka namenode datanode

print_info "Esperando a que los servicios estén listos (60 segundos)..."
for i in {60..1}; do
    echo -ne "\r⏳ Tiempo restante: $i segundos "
    sleep 1
done
echo ""

# Verificar que los servicios estén healthy
print_info "Verificando estado de los servicios..."
sleep 5

KAFKA_HEALTHY=$(docker inspect --format='{{.State.Health.Status}}' kafka 2>/dev/null || echo "starting")
NAMENODE_HEALTHY=$(docker inspect --format='{{.State.Health.Status}}' namenode 2>/dev/null || echo "starting")
DATANODE_HEALTHY=$(docker inspect --format='{{.State.Health.Status}}' datanode 2>/dev/null || echo "starting")

if [ "$KAFKA_HEALTHY" == "healthy" ]; then
    print_success "Kafka está listo"
else
    print_warning "Kafka aún está inicializando (estado: $KAFKA_HEALTHY)"
fi

if [ "$NAMENODE_HEALTHY" == "healthy" ]; then
    print_success "NameNode está listo"
else
    print_warning "NameNode aún está inicializando (estado: $NAMENODE_HEALTHY)"
fi

if [ "$DATANODE_HEALTHY" == "healthy" ]; then
    print_success "DataNode está listo"
else
    print_warning "DataNode aún está inicializando (estado: $DATANODE_HEALTHY)"
fi

echo ""

# Fase 2: Inicializar HDFS
print_info "Fase 2: Inicializando directorios en HDFS..."
chmod +x init-hdfs.sh
./init-hdfs.sh

echo ""

# Fase 3: Resto de servicios
print_info "Fase 3: Iniciando Producer, Consumer y servicios restantes..."
docker compose up -d

print_success "Todos los servicios iniciados"

echo ""
echo "=========================================="
echo "📊 Verificando funcionamiento..."
echo "=========================================="
echo ""

# Esperar un poco más para que Producer y Consumer inicien
print_info "Esperando a que Producer y Consumer inicien (30 segundos)..."
sleep 30

# Verificar Producer
print_info "Verificando Producer..."
if docker logs producer 2>&1 | grep -q "Enviado:"; then
    print_success "Producer está enviando datos a Kafka"
else
    print_warning "Producer aún no ha enviado datos (puede tomar 1-2 minutos)"
fi

# Verificar Consumer
print_info "Verificando Spark Consumer..."
if docker logs spark-consumer 2>&1 | grep -q "Consumer iniciado"; then
    print_success "Consumer está procesando datos"
else
    print_warning "Consumer aún está inicializando"
fi

echo ""
echo "=========================================="
echo "✅ ¡Sistema iniciado correctamente!"
echo "=========================================="
echo ""
echo "📊 Interfaces Web disponibles:"
echo "   • HDFS:  http://localhost:9870"
echo "   • Spark: http://localhost:4040"
echo "   • YARN:  http://localhost:8088"
echo ""
echo "🔍 Comandos útiles:"
echo "   • Ver logs del Producer:"
echo "     docker logs -f producer"
echo ""
echo "   • Ver logs del Consumer:"
echo "     docker logs -f spark-consumer"
echo ""
echo "   • Ver estado de contenedores:"
echo "     docker ps"
echo ""
echo "   • Ver datos en HDFS (después de 2-3 minutos):"
echo "     docker exec namenode hdfs dfs -ls /user/amalia/energy_data/streaming/"
echo ""
echo "   • Detener el sistema:"
echo "     docker compose down"
echo ""
echo "📖 Para más información, consulta INSTALLATION_GUIDE.md"
echo ""
echo "⏱️  Nota: Los datos tardarán 1-2 minutos en aparecer en HDFS"
echo "   El sistema procesa datos cada 60 segundos."
echo ""
