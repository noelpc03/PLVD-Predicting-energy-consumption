# 🗺️ MAPA VISUAL DEL PROYECTO

```
┌─────────────────────────────────────────────────────────────────────┐
│                         TU COMPUTADORA                               │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │                    DOCKER ENGINE                            │    │
│  │                                                             │    │
│  │  ┌──────────────┐      ┌──────────────┐                   │    │
│  │  │  Zookeeper   │──────│    Kafka     │◄─── Producer      │    │
│  │  │   :2181      │      │    :9092     │     (Python)      │    │
│  │  └──────────────┘      └──────┬───────┘                   │    │
│  │                               │                            │    │
│  │                               ↓                            │    │
│  │                        ┌──────────────┐                   │    │
│  │                        │    Spark     │                   │    │
│  │                        │   Consumer   │                   │    │
│  │                        │   :4040 UI   │                   │    │
│  │                        └──────┬───────┘                   │    │
│  │                               │                            │    │
│  │                               ↓                            │    │
│  │  ┌──────────────┐      ┌──────────────┐                   │    │
│  │  │   NameNode   │◄────►│  DataNode    │                   │    │
│  │  │  :9870 UI    │      │    :9864     │                   │    │
│  │  │  :9000 HDFS  │      │              │                   │    │
│  │  └──────┬───────┘      └──────────────┘                   │    │
│  │         │                                                  │    │
│  │         ↓                                                  │    │
│  │  ┌──────────────┐      ┌──────────────┐                   │    │
│  │  │    Hive      │      │    YARN      │                   │    │
│  │  │  Metastore   │      │ :8088 UI     │                   │    │
│  │  │   :9083      │      │              │                   │    │
│  │  └──────────────┘      └──────────────┘                   │    │
│  │                                                             │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                      │
│  Puertos expuestos a tu navegador:                                  │
│  • http://localhost:9870 ← HDFS                                    │
│  • http://localhost:4040 ← Spark                                   │
│  • http://localhost:8088 ← YARN                                    │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 📊 FLUJO DE DATOS DETALLADO

```
PASO 1: CARGA DEL DATASET
┌─────────────────────────┐
│ household_power_        │
│ consumption.txt         │
│ (127 MB, 2M registros)  │
└───────────┬─────────────┘
            │
            ↓
┌─────────────────────────┐
│ data/dataset.txt        │
│ (copiado por start.sh)  │
└───────────┬─────────────┘
            │
            │
PASO 2: PRODUCER (Contenedor Python)
            │
            ↓
┌─────────────────────────┐
│ producer/data_loader.py │
│ • Lee CSV con Pandas    │
│ • Limpia nulos          │
│ • Crea timestamp        │
└───────────┬─────────────┘
            │
            ↓
┌─────────────────────────┐
│ producer/               │
│ message_builder.py      │
│ • Convierte a JSON      │
│ {"datetime": "...",     │
│  "global_active_power"} │
└───────────┬─────────────┘
            │
            ↓ (cada 5 segundos)
┌─────────────────────────┐
│ Kafka Topic             │
│ "energy_stream"         │
│ Buffer de mensajes      │
└───────────┬─────────────┘
            │
            │
PASO 3: CONSUMER (Contenedor Spark)
            │
            ↓ (cada 60 segundos)
┌─────────────────────────┐
│ consumer/src/           │
│ kafka_reader.py         │
│ • Lee stream de Kafka   │
│ • Parsea JSON           │
└───────────┬─────────────┘
            │
            ↓
┌─────────────────────────┐
│ consumer/src/           │
│ data_transformer.py     │
│ • Limpia datos          │
│ • Valida rangos         │
│ • Agrega year/month/day │
└───────────┬─────────────┘
            │
            ↓
┌─────────────────────────┐
│ consumer/src/           │
│ hdfs_writer.py          │
│ • Escribe a HDFS        │
│ • Formato: Parquet      │
│ • Particionado por      │
│   fecha/hora            │
└───────────┬─────────────┘
            │
            │
PASO 4: ALMACENAMIENTO (HDFS)
            │
            ↓
┌─────────────────────────┐
│ HDFS Storage            │
│ hdfs://namenode:9000/   │
│ user/amalia/energy_data │
│ /streaming/             │
│                         │
│ year=2006/              │
│   month=12/             │
│     day=16/             │
│       hour=17/          │
│         part-xxx.parquet│
└───────────┬─────────────┘
            │
            │
PASO 5: HIVE (SQL sobre HDFS)
            │
            ↓
┌─────────────────────────┐
│ Hive Table              │
│ "energy_data"           │
│ • Tabla externa         │
│ • Apunta a HDFS         │
│ • Permite SQL           │
└───────────┬─────────────┘
            │
            ↓
┌─────────────────────────┐
│ Consultas SQL           │
│ SELECT * FROM           │
│ energy_data WHERE       │
│ year = 2007             │
└─────────────────────────┘
```

---

## 🎮 COMANDOS ESENCIALES

### Para iniciar todo:
```bash
./start.sh
```

### Para verificar requisitos:
```bash
./check-requirements.sh
```

### Para monitorear:
```bash
# Ver todos los contenedores
docker ps

# Ver logs del Producer
docker logs -f producer

# Ver logs del Consumer
docker logs -f spark-consumer

# Ver uso de recursos
docker stats
```

### Para verificar datos:
```bash
# Listar archivos en HDFS
docker exec namenode hdfs dfs -ls /user/amalia/energy_data/streaming/

# Ver estructura completa
docker exec namenode hdfs dfs -ls -R /user/amalia/energy_data/streaming/ | head -30

# Contar archivos
docker exec namenode hdfs dfs -count /user/amalia/energy_data/streaming/
```

### Para consultar con SQL:
```bash
# Entrar a Spark SQL
docker exec -it spark-consumer /opt/spark/bin/spark-sql --master local

# Dentro de Spark SQL:
SHOW TABLES;
SELECT COUNT(*) FROM energy_data;
SELECT * FROM energy_data LIMIT 10;
EXIT;
```

### Para detener:
```bash
cd docker

# Detener (mantiene datos)
docker compose stop

# Detener y eliminar contenedores (mantiene volúmenes)
docker compose down

# Eliminar TODO incluyendo datos
docker compose down -v
```

---

## 📂 ESTRUCTURA DE ARCHIVOS

```
PLVD-Predicting-energy-consumption/
│
├── 📄 README.md                    ← Descripción general
├── 📄 QUICK_START.md              ← Esta guía (inicio rápido)
├── 📄 INSTALLATION_GUIDE.md       ← Instalación completa
├── 🔧 check-requirements.sh       ← Verifica requisitos
├── 🚀 start.sh                    ← Inicia todo automáticamente
│
├── 📁 data/
│   └── dataset.txt                ← Dataset (127 MB)
│
├── 📁 producer/                   ← Código del Producer
│   ├── producer.py                ← Script principal
│   ├── data_loader.py             ← Carga CSV
│   ├── message_builder.py         ← Crea JSON
│   ├── kafka_client.py            ← Envía a Kafka
│   ├── config.py                  ← Configuración
│   └── requirements.txt           ← Dependencias Python
│
├── 📁 consumer/                   ← Código del Consumer
│   └── src/
│       ├── consumer.py            ← Script principal Spark
│       ├── kafka_reader.py        ← Lee de Kafka
│       ├── data_transformer.py    ← Transforma datos
│       ├── hdfs_writer.py         ← Escribe a HDFS
│       ├── hive_connector.py      ← Configura Hive
│       └── config.py              ← Configuración
│
├── 📁 docker/                     ← Configuración Docker
│   ├── docker-compose.yml         ← Define todos los servicios
│   ├── init-hdfs.sh               ← Inicializa HDFS
│   ├── FIXES_APPLIED.md           ← Correcciones aplicadas
│   └── spark-consumer/
│       └── Dockerfile             ← Imagen de Spark
│
├── 📁 spark_jobs/                 ← Jobs de análisis
│   ├── features.py                ← Feature engineering
│   ├── clean_data.py              ← Limpieza de datos
│   └── query_examples.py          ← Ejemplos de consultas
│
└── 📁 board/                      ← Dashboard (pendiente)
    └── app.py                     ← Aplicación web
```

---

## ⏱️ TIMELINE DE EJECUCIÓN

```
Tiempo    Evento
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
00:00     ./start.sh ejecutado
00:05     Docker construyendo imágenes...
00:10     Imágenes construidas
00:15     Zookeeper iniciado
00:20     Kafka iniciado (esperando healthy)
00:30     HDFS iniciado (NameNode + DataNode)
00:45     Kafka healthy ✓
00:50     HDFS healthy ✓
00:55     init-hdfs.sh ejecutado
01:00     Directorios HDFS creados ✓
01:05     Producer iniciado
01:10     Consumer (Spark) iniciado
01:20     Producer enviando primer mensaje
01:25     Producer enviando segundo mensaje
01:30     Producer enviando tercer mensaje
01:35     Consumer procesa primer batch (3 mensajes)
01:40     Datos escritos en HDFS ✓
02:00     Tabla Hive disponible ✓
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

A partir de aquí:
• Producer envía 1 mensaje cada 5 segundos
• Consumer procesa batch cada 60 segundos
• Datos se acumulan en HDFS continuamente
```

---

## 🔢 ESTADÍSTICAS DEL PROYECTO

**Dataset:**
- Tamaño: 127 MB
- Registros: 2,075,259
- Periodo: 2006-2010 (4 años)
- Granularidad: 1 minuto

**Procesamiento:**
- Velocidad de envío: 1 mensaje / 5 segundos = 12 msg/min
- Velocidad de procesamiento: Batch cada 60 segundos
- Formato almacenamiento: Parquet (comprimido ~10x)
- Particionado: Año → Mes → Día → Hora

**Recursos:**
- Contenedores: 10
- RAM recomendada: 8 GB
- Disco: ~20 GB
- CPU: 4 cores

**Puertos:**
- 2181: Zookeeper
- 9092: Kafka
- 9870: HDFS Web UI
- 9000: HDFS
- 4040: Spark UI
- 8088: YARN UI
- 9083: Hive Metastore

---

## 🎯 CHECKLIST DE VERIFICACIÓN

Completa después de ejecutar `./start.sh`:

### Servicios Base (primeros 2 minutos)
- [ ] Zookeeper corriendo: `docker ps | grep zookeeper`
- [ ] Kafka healthy: `docker ps | grep kafka` → debe decir "(healthy)"
- [ ] NameNode healthy: `docker ps | grep namenode` → debe decir "(healthy)"
- [ ] DataNode healthy: `docker ps | grep datanode` → debe decir "(healthy)"

### Servicios de Procesamiento (minutos 3-5)
- [ ] Producer corriendo: `docker ps | grep producer`
- [ ] Consumer corriendo: `docker ps | grep spark-consumer`
- [ ] Hive corriendo: `docker ps | grep hive`
- [ ] YARN corriendo: `docker ps | grep yarn` o `resourcemanager`

### Funcionalidad (después de 5 minutos)
- [ ] Producer enviando: `docker logs producer | grep "Enviado:"`
- [ ] Consumer iniciado: `docker logs spark-consumer | grep "Consumer iniciado"`
- [ ] HDFS accesible: Abrir http://localhost:9870
- [ ] Directorios creados: `docker exec namenode hdfs dfs -ls /user/amalia/`
- [ ] Datos en HDFS: `docker exec namenode hdfs dfs -ls /user/amalia/energy_data/streaming/`
- [ ] Archivos Parquet: Deberías ver archivos `.parquet` en HDFS

### Interfaces Web
- [ ] HDFS UI funciona: http://localhost:9870
- [ ] Spark UI funciona: http://localhost:4040
- [ ] YARN UI funciona: http://localhost:8088

---

## 🆘 AYUDA RÁPIDA

**¿Algo no funciona?**

1. Ver logs: `docker logs <nombre-contenedor>`
2. Verificar estado: `docker ps`
3. Reiniciar servicio: `docker compose restart <servicio>`
4. Reiniciar todo: `cd docker && docker compose restart`
5. Limpiar y reiniciar: `docker compose down && ./start.sh`

**¿Contenedor no está "healthy"?**
```bash
# Ver detalles del healthcheck
docker inspect <nombre-contenedor> | grep -A 20 Health
```

**¿Puerto ocupado?**
```bash
# Ver qué usa el puerto
sudo lsof -i :<numero-puerto>
```

---

¡Éxito! 🎉
