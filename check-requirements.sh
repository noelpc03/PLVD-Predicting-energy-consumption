#!/bin/bash
# Script para verificar que todos los requisitos estén instalados

echo "=========================================="
echo "🔍 Verificación de Requisitos - PLVD"
echo "=========================================="
echo ""

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

ERRORS=0
WARNINGS=0

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
    ((ERRORS++))
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
    ((WARNINGS++))
}

# ==== 1. Docker ====
echo "1️⃣  Verificando Docker..."
if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version | cut -d' ' -f3 | cut -d',' -f1)
    print_success "Docker instalado (versión $DOCKER_VERSION)"
    
    # Verificar que Docker está corriendo
    if docker ps &> /dev/null; then
        print_success "Docker está corriendo"
    else
        print_error "Docker está instalado pero no está corriendo"
        echo "   💡 Solución: Ejecuta 'sudo systemctl start docker'"
    fi
    
    # Verificar permisos
    if docker ps &> /dev/null; then
        print_success "Usuario tiene permisos para usar Docker"
    else
        if sudo docker ps &> /dev/null; then
            print_warning "Requieres sudo para usar Docker"
            echo "   💡 Solución: Ejecuta 'sudo usermod -aG docker \$USER' y reinicia sesión"
        fi
    fi
else
    print_error "Docker no está instalado"
    echo "   💡 Solución: Consulta INSTALLATION_GUIDE.md, PASO 1"
fi

echo ""

# ==== 2. Docker Compose ====
echo "2️⃣  Verificando Docker Compose..."
if command -v docker compose &> /dev/null; then
    print_success "Docker Compose instalado (plugin)"
elif command -v docker-compose &> /dev/null; then
    print_success "Docker Compose instalado (standalone)"
else
    print_error "Docker Compose no está instalado"
    echo "   💡 Solución: Consulta INSTALLATION_GUIDE.md, PASO 1"
fi

echo ""

# ==== 3. Recursos del Sistema ====
echo "3️⃣  Verificando recursos del sistema..."

# Memoria RAM
if command -v free &> /dev/null; then
    TOTAL_RAM=$(free -g | awk '/^Mem:/{print $2}')
    if [ "$TOTAL_RAM" -ge 8 ]; then
        print_success "RAM suficiente: ${TOTAL_RAM}GB (mínimo 8GB)"
    elif [ "$TOTAL_RAM" -ge 6 ]; then
        print_warning "RAM limitada: ${TOTAL_RAM}GB (recomendado 8GB o más)"
        echo "   💡 El sistema puede funcionar lento"
    else
        print_error "RAM insuficiente: ${TOTAL_RAM}GB (mínimo 8GB requerido)"
        echo "   💡 Solución: Cierra aplicaciones o aumenta RAM"
    fi
else
    print_warning "No se pudo verificar RAM (comando 'free' no disponible)"
fi

# Espacio en disco
DISK_SPACE=$(df -h . | awk 'NR==2 {print $4}' | sed 's/G//')
if [ ! -z "$DISK_SPACE" ]; then
    if [ "${DISK_SPACE%.*}" -ge 20 ]; then
        print_success "Espacio en disco: ${DISK_SPACE}GB disponible (mínimo 20GB)"
    else
        print_warning "Espacio limitado: ${DISK_SPACE}GB disponible (recomendado 20GB)"
    fi
fi

# CPU
CPU_CORES=$(nproc 2>/dev/null || sysctl -n hw.ncpu 2>/dev/null || echo "unknown")
if [ "$CPU_CORES" != "unknown" ]; then
    if [ "$CPU_CORES" -ge 4 ]; then
        print_success "CPU cores: $CPU_CORES (mínimo 4)"
    else
        print_warning "CPU cores limitados: $CPU_CORES (recomendado 4 o más)"
    fi
fi

echo ""

# ==== 4. Dataset ====
echo "4️⃣  Verificando dataset..."
if [ -f "data/dataset.txt" ]; then
    DATASET_SIZE=$(du -h data/dataset.txt | cut -f1)
    print_success "Dataset encontrado: data/dataset.txt (${DATASET_SIZE})"
elif [ -f "household_power_consumption.txt" ]; then
    print_warning "Dataset en ubicación original: household_power_consumption.txt"
    echo "   💡 Se moverá automáticamente al ejecutar start.sh"
else
    print_error "Dataset no encontrado"
    echo "   💡 Solución: Descarga 'household_power_consumption.txt' y colócalo en la raíz"
fi

echo ""

# ==== 5. Estructura del Proyecto ====
echo "5️⃣  Verificando estructura del proyecto..."

check_dir() {
    if [ -d "$1" ]; then
        print_success "Directorio: $1"
    else
        print_error "Falta directorio: $1"
    fi
}

check_file() {
    if [ -f "$1" ]; then
        print_success "Archivo: $1"
    else
        print_error "Falta archivo: $1"
    fi
}

check_dir "producer"
check_dir "consumer"
check_dir "docker"
check_file "docker/docker-compose.yml"
check_file "docker/init-hdfs.sh"
check_file "producer/producer.py"
check_file "consumer/src/consumer.py"

echo ""

# ==== 6. Puertos ====
echo "6️⃣  Verificando puertos necesarios..."

check_port() {
    PORT=$1
    SERVICE=$2
    if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1 || netstat -tuln 2>/dev/null | grep -q ":$PORT "; then
        print_warning "Puerto $PORT ($SERVICE) ya está en uso"
        echo "   💡 Verifica con: sudo lsof -i :$PORT"
    else
        print_success "Puerto $PORT ($SERVICE) disponible"
    fi
}

# Solo verificamos puertos si los comandos están disponibles
if command -v lsof &> /dev/null || command -v netstat &> /dev/null; then
    check_port 9092 "Kafka"
    check_port 9870 "HDFS"
    check_port 4040 "Spark UI"
else
    print_warning "No se pudieron verificar puertos (lsof/netstat no disponible)"
fi

echo ""

# ==== 7. Configuración de Docker Desktop (si aplica) ====
if [[ "$OSTYPE" == "darwin"* ]] || [[ "$OSTYPE" == "msys" ]]; then
    echo "7️⃣  Verificando Docker Desktop..."
    if pgrep -x "Docker" > /dev/null || pgrep -x "Docker Desktop" > /dev/null; then
        print_success "Docker Desktop está corriendo"
        print_warning "Asegúrate de configurar al menos 8GB RAM en Docker Desktop"
        echo "   💡 Settings → Resources → Memory: 8GB+"
    else
        print_warning "Docker Desktop no parece estar corriendo"
    fi
    echo ""
fi

# ==== RESUMEN ====
echo "=========================================="
echo "📊 Resumen"
echo "=========================================="
echo ""

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✅ ¡Perfecto! Tu sistema está listo.${NC}"
    echo ""
    echo "🚀 Siguiente paso: Ejecuta ./start.sh para iniciar el proyecto"
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠️  Tienes $WARNINGS advertencia(s).${NC}"
    echo "   El sistema puede funcionar, pero con limitaciones."
    echo ""
    echo "🚀 Puedes intentar ejecutar ./start.sh"
else
    echo -e "${RED}❌ Tienes $ERRORS error(es) y $WARNINGS advertencia(s).${NC}"
    echo ""
    echo "🔧 Por favor corrige los errores antes de continuar."
    echo "📖 Consulta INSTALLATION_GUIDE.md para instrucciones detalladas."
fi

echo ""
exit $ERRORS
