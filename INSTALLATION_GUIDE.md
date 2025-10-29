# 🚀 Guía Completa de Instalación - PLVD Energy Consumption

## 📋 Requisitos del Sistema

### Hardware Mínimo
- **RAM**: 8 GB (16 GB recomendado)
- **Disco**: 20 GB de espacio libre
- **CPU**: 4 núcleos (8 recomendado)
- **Sistema Operativo**: Linux (Ubuntu/Debian preferido), macOS, o Windows con WSL2

---

## 🛠️ PASO 1: Instalar Docker

### Para Ubuntu/Debian

```bash
# 1. Actualizar repositorios
sudo apt update
sudo apt upgrade -y

# 2. Instalar dependencias
sudo apt install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# 3. Agregar la clave GPG oficial de Docker
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# 4. Configurar el repositorio de Docker
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# 5. Instalar Docker Engine
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# 6. Verificar instalación
sudo docker --version
# Debe mostrar: Docker version 24.x.x o superior

# 7. Agregar tu usuario al grupo docker (para no usar sudo)
sudo usermod -aG docker $USER

# 8. IMPORTANTE: Cerrar sesión y volver a entrar para aplicar cambios
# O ejecutar:
newgrp docker

# 9. Verificar que funciona sin sudo
docker ps
```

### Para Fedora/CentOS/RHEL

```bash
# 1. Instalar Docker
sudo dnf -y install dnf-plugins-core
sudo dnf config-manager --add-repo https://download.docker.com/linux/fedora/docker-ce.repo
sudo dnf install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# 2. Iniciar Docker
sudo systemctl start docker
sudo systemctl enable docker

# 3. Agregar usuario al grupo
sudo usermod -aG docker $USER
newgrp docker
```

### Para macOS

```bash
# 1. Descargar Docker Desktop desde:
# https://www.docker.com/products/docker-desktop/

# 2. Instalar el archivo .dmg descargado

# 3. Abrir Docker Desktop desde Aplicaciones

# 4. Esperar a que inicie completamente (ícono de ballena en la barra superior)

# 5. Verificar instalación en Terminal
docker --version
docker compose version
```

### Para Windows

```bash
# 1. Habilitar WSL2:
# - Abrir PowerShell como Administrador
wsl --install

# 2. Reiniciar el sistema

# 3. Descargar Docker Desktop desde:
# https://www.docker.com/products/docker-desktop/

# 4. Instalar Docker Desktop (asegurar que usa WSL2 backend)

# 5. Abrir Docker Desktop

# 6. Verificar en PowerShell o WSL2 terminal:
docker --version
docker compose version
```

---

## ⚙️ PASO 2: Configurar Docker

### Aumentar recursos de Docker (IMPORTANTE)

#### En Linux:
No requiere configuración adicional, usa recursos del sistema directamente.

#### En macOS/Windows con Docker Desktop:

1. Abrir **Docker Desktop**
2. Ir a **Settings** (⚙️) → **Resources**
3. Configurar:
   - **Memory**: Mínimo 8 GB (recomendado 12 GB)
   - **CPUs**: Mínimo 4 (recomendado 6)
   - **Disk**: Mínimo 20 GB
4. Clic en **Apply & Restart**

---

## 📥 PASO 3: Clonar o Descargar el Proyecto

Si ya tienes el proyecto descargado, sáltate este paso.

### Opción A: Con Git (si tienes acceso al repositorio)

```bash
# Instalar Git si no lo tienes
sudo apt install git  # Ubuntu/Debian
# o
brew install git      # macOS

# Clonar repositorio
git clone https://github.com/noelpc03/PLVD-Predicting-energy-consumption.git
cd PLVD-Predicting-energy-consumption
```

### Opción B: Sin Git

Si ya tienes el proyecto en tu computadora, simplemente navega a la carpeta:

```bash
cd "/home/noel/Disco D/4to_Anno/BigData/PLVD-Predicting-energy-consumption"
```

---

## 📊 PASO 4: Verificar el Dataset

El dataset ya está configurado. Verifica que existe:

```bash
ls -lah data/dataset.txt
```

**Salida esperada**:
```
-rw-rw-r-- 1 noel noel 127M Oct 28 21:47 data/dataset.txt
```

✅ Si ves esto, está correcto.

---

## 🐳 PASO 5: Construir las Imágenes Docker

```bash
# Ir al directorio docker
cd docker

# Construir todas las imágenes necesarias
docker compose build

# Esto tomará 5-10 minutos la primera vez
# Descarga imágenes base (Spark, Hadoop, Kafka, etc.)
```

**Salida esperada**:
```
[+] Building 245.3s (9/9) FINISHED
 => [internal] load build definition from Dockerfile
 => => transferring dockerfile: 234B
 => [internal] load .dockerignore
 ...
 => => naming to docker.io/library/docker-spark-consumer
```

---

## 🚀 PASO 6: Levantar los Servicios

### Estrategia de Inicio Recomendada

#### 6.1. Levantar servicios base primero

```bash
# Desde la carpeta docker/
docker compose up -d zookeeper kafka namenode datanode
```

#### 6.2. Esperar a que estén saludables (2-3 minutos)

```bash
# Monitorear el estado
watch -n 2 'docker ps --format "table {{.Names}}\t{{.Status}}"'

# O sin watch:
docker ps
```

**Espera hasta ver**:
```
CONTAINER ID   IMAGE                    STATUS
zookeeper      ...                      Up 2 minutes
kafka          ...                      Up 2 minutes (healthy)
namenode       ...                      Up 2 minutes (healthy)
datanode       ...                      Up 2 minutes (healthy)
```

Presiona `Ctrl+C` para salir del watch.

#### 6.3. Inicializar HDFS

```bash
# Dar permisos de ejecución al script
chmod +x init-hdfs.sh

# Ejecutar inicialización
./init-hdfs.sh
```

**Salida esperada**:
```
🚀 Inicializando HDFS...
⏳ Esperando a que Namenode esté listo...
✅ Namenode listo
✅ Directorios HDFS creados:
drwxr-xr-x   - amalia amalia          0 2025-10-28 20:00 /user/amalia
drwxr-xr-x   - amalia amalia          0 2025-10-28 20:00 /user/amalia/energy_data
✅ Inicialización completada
```

#### 6.4. Levantar servicios restantes

```bash
docker compose up -d
```

Esto levanta:
- `resourcemanager`
- `nodemanager`
- `hive-metastore`
- `producer`
- `spark-consumer`

---

## 📊 PASO 7: Verificar que Todo Funciona

### 7.1. Ver estado de contenedores

```bash
docker ps
```

**Deberías ver 10 contenedores corriendo**:
```
CONTAINER ID   IMAGE                    NAMES              STATUS
...            ...                      zookeeper          Up 5 minutes
...            ...                      kafka              Up 5 minutes (healthy)
...            ...                      namenode           Up 5 minutes (healthy)
...            ...                      datanode           Up 5 minutes (healthy)
...            ...                      resourcemanager    Up 3 minutes
...            ...                      nodemanager        Up 3 minutes
...            ...                      hive-metastore     Up 3 minutes
...            ...                      producer           Up 3 minutes
...            ...                      spark-consumer     Up 3 minutes
```

### 7.2. Verificar logs del Producer

```bash
docker logs -f producer
```

**Salida esperada** (después de ~20 segundos):
```
Esperando a que Kafka esté listo...
Kafka listo, arrancando productor
📤 Inicio de envío de 2075259 registros cada 5.0 segundos al topic 'energy_stream'...
📤 Enviado: {"datetime": "2006-12-16 17:24:00", "global_active_power": 4.216, ...}
📤 Enviado: {"datetime": "2006-12-16 17:25:00", "global_active_power": 5.360, ...}
📤 Enviado: {"datetime": "2006-12-16 17:26:00", "global_active_power": 5.374, ...}
```

✅ Si ves esto, el Producer está funcionando.

Presiona `Ctrl+C` para salir.

### 7.3. Verificar logs del Consumer (Spark)

```bash
docker logs -f spark-consumer
```

**Salida esperada** (después de ~40 segundos):
```
Esperando servicios...
Servicios listos, iniciando Spark Consumer...
25/10/28 20:05:23 INFO SparkContext: Running Spark version 3.5.0
🚀 Iniciando Consumer de datos energéticos...
📡 Broker Kafka: kafka:9092
📨 Topic: energy_stream
💾 HDFS: hdfs://namenode:9000
🗃️  Configurando tablas de Hive...
✅ Tabla Hive 'energy_data' creada/actualizada
📖 Leyendo stream de Kafka...
🔄 Transformando datos...
💾 Escribiendo en HDFS...
✅ Consumer iniciado correctamente
📊 Procesando stream continuamente...
```

✅ Si ves esto, el Consumer está procesando datos.

Presiona `Ctrl+C` para salir.

### 7.4. Verificar interfaces web

Abre tu navegador y verifica estas URLs:

1. **HDFS Web UI**: http://localhost:9870
   - Deberías ver la interfaz de Hadoop
   - Ir a **Utilities** → **Browse the file system**
   - Navegar a `/user/amalia/energy_data/streaming/`
   - Después de 1-2 minutos verás carpetas como `year=2006/`

2. **Spark UI**: http://localhost:4040
   - Muestra jobs de Spark en ejecución
   - Ver **Streaming** tab para estadísticas en tiempo real

3. **YARN Resource Manager**: http://localhost:8088
   - Panel de gestión de recursos del cluster

---

## 🔍 PASO 8: Verificar Datos en HDFS

Después de 2-3 minutos de ejecución:

```bash
# Listar directorios creados
docker exec namenode hdfs dfs -ls /user/amalia/energy_data/streaming/

# Ver estructura de particiones
docker exec namenode hdfs dfs -ls -R /user/amalia/energy_data/streaming/ | head -20
```

**Salida esperada**:
```
drwxr-xr-x   - root supergroup          0 2025-10-28 20:06 /user/amalia/energy_data/streaming/year=2006
drwxr-xr-x   - root supergroup          0 2025-10-28 20:06 /user/amalia/energy_data/streaming/year=2006/month=12
drwxr-xr-x   - root supergroup          0 2025-10-28 20:06 /user/amalia/energy_data/streaming/year=2006/month=12/day=16
drwxr-xr-x   - root supergroup          0 2025-10-28 20:06 /user/amalia/energy_data/streaming/year=2006/month=12/day=16/hour=17
-rw-r--r--   3 root supergroup       1234 2025-10-28 20:06 /user/amalia/energy_data/streaming/year=2006/month=12/day=16/hour=17/part-00000-xxx.parquet
```

✅ Si ves archivos `.parquet`, ¡funciona!

---

## 📊 PASO 9: Consultar Datos con Spark SQL

```bash
# Entrar al contenedor de Spark
docker exec -it spark-consumer /bin/bash

# Iniciar Spark SQL
/opt/spark/bin/spark-sql --master local

# Dentro de Spark SQL, ejecutar:
```

```sql
-- Ver tablas disponibles
SHOW TABLES;

-- Contar registros totales
SELECT COUNT(*) as total_records FROM energy_data;

-- Ver primeros 10 registros
SELECT * FROM energy_data LIMIT 10;

-- Consumo promedio por año
SELECT 
    year, 
    ROUND(AVG(global_active_power), 2) as avg_power,
    COUNT(*) as records
FROM energy_data 
GROUP BY year 
ORDER BY year;

-- Salir
EXIT;
```

---

## 🛑 PASO 10: Detener el Sistema

### Detener temporalmente (mantiene datos)

```bash
cd docker
docker compose stop
```

### Reiniciar después

```bash
docker compose start
```

### Detener y eliminar contenedores (mantiene datos)

```bash
docker compose down
```

### Eliminar TODO (contenedores + datos)

```bash
docker compose down -v
```

⚠️ **CUIDADO**: Esto elimina todos los datos procesados en HDFS.

---

## 🐛 Solución de Problemas Comunes

### Error: "Cannot connect to the Docker daemon"

```bash
# Verificar que Docker está corriendo
sudo systemctl status docker

# Si no está corriendo, iniciarlo
sudo systemctl start docker

# Verificar que tu usuario está en el grupo docker
groups $USER

# Si no ves "docker", agregarlo
sudo usermod -aG docker $USER
newgrp docker
```

### Error: "port is already allocated"

```bash
# Ver qué está usando el puerto (ejemplo puerto 9092)
sudo lsof -i :9092

# Matar el proceso
sudo kill -9 <PID>

# O cambiar el puerto en docker-compose.yml
```

### Error: Producer dice "No brokers available"

```bash
# Verificar que Kafka está healthy
docker ps | grep kafka

# Ver logs de Kafka
docker logs kafka

# Si Kafka no está healthy, reiniciarlo
docker compose restart kafka

# Esperar 30 segundos y verificar
docker ps | grep kafka
```

### Error: Consumer no puede escribir a HDFS

```bash
# Verificar que NameNode está healthy
docker ps | grep namenode

# Re-inicializar HDFS
./init-hdfs.sh

# Dar permisos completos (temporal)
docker exec namenode hdfs dfs -chmod -R 777 /user/amalia
```

### Error: "Out of memory"

```bash
# Aumentar memoria de Docker Desktop (macOS/Windows)
# Settings → Resources → Memory: 12 GB

# En Linux, verificar memoria disponible
free -h

# Cerrar aplicaciones que consuman mucha RAM
```

### Logs de error en Spark Consumer

```bash
# Ver logs completos
docker logs spark-consumer

# Si hay error con packages de Maven
# Limpiar cache de Ivy
docker exec spark-consumer rm -rf /tmp/.ivy2
docker compose restart spark-consumer
```

---

## 📈 Monitoreo en Tiempo Real

### Terminal 1: Logs del Producer
```bash
docker logs -f producer
```

### Terminal 2: Logs del Consumer
```bash
docker logs -f spark-consumer
```

### Terminal 3: Estado de contenedores
```bash
watch -n 2 'docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"'
```

### Terminal 4: Uso de recursos
```bash
watch -n 2 'docker stats'
```

---

## 🎯 Resumen de Comandos Esenciales

```bash
# ==== INICIO ====
cd docker
docker compose build                    # Primera vez solamente
docker compose up -d zookeeper kafka namenode datanode
# Esperar 2 minutos
./init-hdfs.sh
docker compose up -d

# ==== MONITOREO ====
docker ps                               # Ver contenedores
docker logs -f producer                 # Ver logs del producer
docker logs -f spark-consumer           # Ver logs del consumer
docker stats                            # Ver uso de recursos

# ==== VERIFICACIÓN ====
docker exec namenode hdfs dfs -ls /user/amalia/energy_data/streaming/
# Web UIs:
# http://localhost:9870  (HDFS)
# http://localhost:4040  (Spark)

# ==== DETENER ====
docker compose stop                     # Detener (mantiene datos)
docker compose down                     # Detener y eliminar contenedores
docker compose down -v                  # Eliminar TODO incluyendo datos
```

---

## ✅ Checklist Final

Antes de dar por terminada la instalación, verifica:

- [ ] Docker instalado y corriendo: `docker --version`
- [ ] Docker Compose instalado: `docker compose version`
- [ ] Usuario agregado al grupo docker: `groups $USER | grep docker`
- [ ] Dataset existe: `ls data/dataset.txt`
- [ ] Imágenes construidas: `docker images | grep spark-consumer`
- [ ] 10 contenedores corriendo: `docker ps | wc -l` (debe dar 10)
- [ ] Producer enviando datos: `docker logs producer | grep Enviado`
- [ ] Consumer procesando: `docker logs spark-consumer | grep "Consumer iniciado"`
- [ ] HDFS tiene datos: `docker exec namenode hdfs dfs -ls /user/amalia/energy_data/streaming/`
- [ ] Web UI accesible: http://localhost:9870

---

## 📚 Recursos Adicionales

- **Docker Docs**: https://docs.docker.com/
- **Spark Structured Streaming**: https://spark.apache.org/docs/latest/structured-streaming-programming-guide.html
- **Kafka Documentation**: https://kafka.apache.org/documentation/
- **Hadoop HDFS**: https://hadoop.apache.org/docs/stable/hadoop-project-dist/hadoop-hdfs/HdfsUserGuide.html

---

## 🆘 Soporte

Si encuentras algún problema que no está en esta guía:

1. Revisa los logs: `docker logs <nombre-contenedor>`
2. Verifica el estado: `docker ps -a`
3. Consulta el archivo `docker/FIXES_APPLIED.md`
4. Revisa la documentación en `docker/README.md`

---

**¡Listo! Tu sistema de procesamiento de Big Data está funcionando.**

Última actualización: 2025-10-28
