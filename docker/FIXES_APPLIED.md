# 🔧 Correcciones Aplicadas al Docker Compose

## 📋 Resumen de Errores Encontrados

### ❌ **Error #1: Carpeta `/data/` no existía**
**Problema**: El docker-compose.yml intentaba montar `../data:/app/data` pero la carpeta no existía.

**Solución Aplicada**: 
```bash
mkdir -p data
cp household_power_consumption.txt data/dataset.txt
```

---

### ❌ **Error #2: Ruta incorrecta del Producer**
**Problema**: 
```yaml
volumes:
  - ./producer:/app  # ❌ ./producer no existe en docker/
```

**Solución Aplicada**:
```yaml
volumes:
  - ../producer:/app  # ✅ Ahora apunta a la raíz del proyecto
```

---

### ❌ **Error #3: Faltaban healthchecks**
**Problema**: Los servicios dependientes iniciaban antes de que Kafka y HDFS estuvieran listos.

**Solución Aplicada**:
- Agregado healthcheck a Kafka
- Agregado healthcheck a NameNode
- Agregado healthcheck a DataNode
- Modificado `depends_on` para usar `condition: service_healthy`

---

### ❌ **Error #4: Puerto HDFS no expuesto**
**Problema**: El puerto 9000 de HDFS no estaba mapeado, causando errores de conexión.

**Solución Aplicada**:
```yaml
ports:
  - "9870:9870" # Web UI
  - "9000:9000" # HDFS port ✅ AGREGADO
```

---

### ❌ **Error #5: Tiempos de espera muy cortos**
**Problema**: Producer y Consumer intentaban conectarse antes de que los servicios estuvieran listos.

**Solución Aplicada**:
- Producer: sleep 15 (suficiente con healthcheck)
- Consumer: sleep 30 (aumentado de 15 a 30)
- Agregado `restart: on-failure` a ambos

---

## ✅ Mejoras Adicionales Implementadas

1. **Variables de entorno de HDFS**:
   - Agregado `CORE_CONF_fs_defaultFS=hdfs://namenode:9000`

2. **Healthcheck mejorado para NameNode**:
   - Usa curl para verificar Web UI
   - `start_period: 60s` para dar tiempo de inicialización

3. **Política de reintentos**:
   - Agregado `restart: on-failure` a Producer y Consumer
   - Si fallan, Docker los reinicia automáticamente

4. **Tiempos de healthcheck optimizados**:
   - Kafka: `start_period: 40s`
   - NameNode: `start_period: 60s`
   - DataNode: `start_period: 40s` (ya existía)

---

## 🚀 Instrucciones de Uso

### 1. Limpiar estado anterior (si existe)
```bash
cd docker
docker compose down -v
```

### 2. Construir imágenes
```bash
docker compose build
```

### 3. Levantar servicios base primero
```bash
docker compose up -d zookeeper kafka namenode datanode
```

### 4. Esperar a que estén saludables
```bash
docker ps
# Verificar que STATUS muestre "healthy" para kafka, namenode, datanode
```

### 5. Inicializar HDFS
```bash
./init-hdfs.sh
```

### 6. Levantar resto de servicios
```bash
docker compose up -d
```

### 7. Verificar logs
```bash
docker logs -f producer
docker logs -f spark-consumer
```

---

## 🔍 Verificación de Funcionamiento

### Verificar Kafka
```bash
# Ver logs
docker logs kafka

# Debe mostrar:
# [KafkaServer id=1] started (kafka.server.KafkaServer)
```

### Verificar HDFS
```bash
# Acceder a Web UI
http://localhost:9870

# Ver directorios
docker exec namenode hdfs dfs -ls /user/amalia/energy_data/
```

### Verificar Producer
```bash
docker logs producer | tail -20

# Debe mostrar:
# 📤 Enviado: {"datetime": "...", "global_active_power": ...}
```

### Verificar Consumer
```bash
docker logs spark-consumer | tail -50

# Debe mostrar:
# ✅ Consumer iniciado correctamente
# 📊 Procesando stream continuamente...
```

---

## 🐛 Troubleshooting

### Si Producer falla con "No brokers available"
```bash
# Verificar que Kafka esté healthy
docker ps | grep kafka

# Si no está healthy, ver logs
docker logs kafka

# Reiniciar Kafka
docker compose restart kafka
```

### Si Consumer no puede conectar a HDFS
```bash
# Verificar que NameNode esté healthy
docker ps | grep namenode

# Ver Web UI
http://localhost:9870

# Verificar conectividad
docker exec spark-consumer ping namenode -c 3
```

### Si hay errores de permisos en HDFS
```bash
# Re-ejecutar inicialización
./init-hdfs.sh

# O manualmente:
docker exec namenode hdfs dfs -chmod -R 777 /user/amalia
```

---

## 📊 Arquitectura Final

```
┌─────────────┐
│  Zookeeper  │
│   :2181     │
└──────┬──────┘
       │
┌──────▼──────┐      ┌──────────────┐
│    Kafka    │◄─────┤   Producer   │
│   :9092     │      │  (Python)    │
└──────┬──────┘      └──────────────┘
       │
       │
┌──────▼───────────┐
│ Spark Consumer   │
│  :4040 (UI)      │
└──────┬───────────┘
       │
       │
┌──────▼──────┐     ┌──────────────┐
│  NameNode   │◄───►│  DataNode    │
│  :9870 :9000│     │  :9864       │
└──────┬──────┘     └──────────────┘
       │
┌──────▼──────┐
│    Hive     │
│  Metastore  │
│   :9083     │
└─────────────┘
```

---

## ✅ Checklist de Validación

- [x] Carpeta `data/` creada con `dataset.txt`
- [x] Rutas del Producer corregidas
- [x] Healthchecks agregados a servicios críticos
- [x] Puerto 9000 de HDFS expuesto
- [x] Tiempos de espera aumentados
- [x] Políticas de reinicio configuradas
- [x] Script `init-hdfs.sh` verificado

---

## 📝 Notas Importantes

1. **Primera ejecución**: Los contenedores tardarán ~2-3 minutos en estar completamente listos
2. **Memoria**: Asegurar al menos 8GB RAM disponibles para Docker
3. **Dataset**: El archivo debe estar en `data/dataset.txt` (119 MB aprox)
4. **Logs**: Monitorear los logs de cada servicio durante la primera ejecución

---

Fecha de corrección: 2025-10-28
