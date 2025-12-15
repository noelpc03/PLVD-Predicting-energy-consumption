# 🔍 ANÁLISIS COMPLETO DE ERRORES DEL PROYECTO

## 📋 RESUMEN EJECUTIVO

El proyecto tiene **múltiples errores críticos** que impiden su funcionamiento. El principal problema es una **inconsistencia en la configuración del nombre del cluster HDFS** entre diferentes componentes del sistema.

---

## ❌ ERRORES CRÍTICOS POR CAPA

### 🔴 **CAPA 1: INFRAESTRUCTURA HDFS - ERROR CRÍTICO**

#### **Problema Principal: Inconsistencia en el nombre del cluster HDFS**

**Descripción:**
- El `docker-compose.yml` configura HDFS con el nombre de cluster **`mycluster`** (`hdfs://mycluster`)
- Sin embargo, múltiples componentes usan **`namenode:9000`** (`hdfs://namenode:9000`)
- Esto causa que los componentes no puedan conectarse correctamente a HDFS

**Ubicaciones del error:**

1. **docker-compose.yml (líneas 111, 162, 209, 234, 259)**
   ```yaml
   - CORE_CONF_fs_defaultFS=hdfs://mycluster  ✅ CORRECTO
   ```

2. **docker-compose.yml - DataNodes (líneas 289, 324, 356)**
   ```yaml
   - CORE_CONF_fs_defaultFS=hdfs://namenode:9000  ❌ INCORRECTO
   ```
   **Debería ser:** `hdfs://mycluster`

3. **docker/init-hdfs.sh (líneas 21, 33-44)**
   ```bash
   hdfs dfs -fs hdfs://namenode:9000  ❌ INCORRECTO
   ```
   **Debería ser:** `hdfs://mycluster`

4. **consumer/src/config.py (línea 26)**
   ```python
   HDFS_PATH = f"hdfs://{HDFS_NAMENODE}:{HDFS_PORT}{HDFS_BASE_PATH}"
   # Esto genera: hdfs://namenode:9000/...  ❌ INCORRECTO
   ```
   **Debería ser:** `hdfs://mycluster/...`

5. **consumer/src/consumer.py (líneas 25-26)**
   ```python
   .config("spark.hadoop.fs.defaultFS", f"hdfs://{HDFS_NAMENODE}:{HDFS_PORT}")
   # Esto genera: hdfs://namenode:9000  ❌ INCORRECTO
   ```
   **Debería ser:** `hdfs://mycluster`

6. **board/hive_connector.py (línea 22)**
   ```python
   HDFS_DATA_PATH = f"hdfs://{HDFS_NAMENODE}:{HDFS_PORT}/user/{HDFS_USER}/{PROJECT_NAME}/streaming"
   # Esto genera: hdfs://namenode:9000/...  ❌ INCORRECTO
   ```
   **Debería ser:** `hdfs://mycluster/...`

7. **board/spark_query.py y consumer/spark_query.py (línea 21)**
   ```python
   .config("spark.hadoop.fs.defaultFS", sys.argv[2] if len(sys.argv) > 2 else "hdfs://namenode:9000")
   # Default incorrecto  ❌ INCORRECTO
   ```
   **Debería ser:** `hdfs://mycluster`

---

### 🔴 **CAPA 2: CONSUMER (SPARK) - ERRORES CRÍTICOS**

#### **Error 1: Configuración incorrecta del objeto Config**

**Ubicación:** `consumer/src/consumer.py` (líneas 48, 56)

**Problema:**
```python
df_stream = create_kafka_stream(spark, type('Config', (), globals()))
df_transformed = transform_data(df_stream)
query = write_to_hdfs(df_transformed, type('Config', (), globals()), CHECKPOINT_LOCATION)
```

**Análisis:**
- `type('Config', (), globals())` es un hack que crea un objeto dinámico con todas las variables globales
- Esto es frágil y propenso a errores
- Las funciones `create_kafka_stream` y `write_to_hdfs` esperan un objeto `config` con atributos específicos
- El objeto creado dinámicamente puede no tener los atributos correctos

**Solución:**
- Pasar directamente las variables de configuración o crear un objeto Config apropiado
- O mejor: modificar las funciones para usar directamente las variables del módulo `config`

#### **Error 2: HDFS Path incorrecto en hdfs_writer.py**

**Ubicación:** `consumer/src/hdfs_writer.py` (línea 20)

**Problema:**
```python
hdfs_output_path = f"{config.HDFS_PATH}/streaming"
```

**Análisis:**
- `config.HDFS_PATH` viene del objeto dinámico creado con `type('Config', (), globals())`
- Si el objeto no tiene el atributo correcto, esto fallará
- Además, `HDFS_PATH` ya incluye el path base, por lo que agregar `/streaming` puede duplicar paths

**Solución:**
- Usar directamente `HDFS_PATH` del módulo `config` importado
- O construir el path correctamente

#### **Error 3: Kafka Reader usa objeto config incorrecto**

**Ubicación:** `consumer/src/kafka_reader.py` (líneas 33-34)

**Problema:**
```python
.option("kafka.bootstrap.servers", config.KAFKA_BROKER)
.option("subscribe", config.KAFKA_TOPIC)
```

**Análisis:**
- Similar al problema anterior, el objeto `config` puede no tener los atributos correctos
- Debería usar directamente las variables del módulo `config`

---

### 🔴 **CAPA 3: PRODUCER - ERRORES MENORES**

#### **Error 1: Path del dataset puede no existir**

**Ubicación:** `producer/data_loader.py` (línea 9)

**Problema:**
```python
df = pd.read_csv(DATASET_PATH, sep=';', low_memory=False)
```

**Análisis:**
- Si `DATASET_PATH` no existe o es incorrecto, el producer fallará sin un mensaje claro
- No hay validación previa del archivo

**Solución:**
- Agregar validación de existencia del archivo antes de leerlo

#### **Error 2: Mensaje de error poco informativo en kafka_client.py**

**Ubicación:** `producer/kafka_client.py` (línea 10)

**Problema:**
```python
bootstrap_servers=KAFKA_BROKER,
```

**Análisis:**
- Si `KAFKA_BROKER` es una lista de brokers separados por comas, `KafkaProducer` debería manejarlo correctamente
- Pero si hay un error de conexión, el mensaje puede no ser claro

---

### 🔴 **CAPA 4: DASHBOARD - ERRORES CRÍTICOS**

#### **Error 1: Path incorrecto para spark_query.py**

**Ubicación:** `board/hive_connector.py` (línea 37)

**Problema:**
```python
'/app/consumer/spark_query.py',
```

**Análisis:**
- El dashboard intenta ejecutar `/app/consumer/spark_query.py` dentro del contenedor `spark-consumer`
- Pero según el `docker-compose.yml`, el volumen montado es:
  ```yaml
  - ../consumer:/app/consumer
  ```
- El archivo `spark_query.py` existe tanto en `consumer/` como en `board/`, pero el path puede no ser correcto

**Solución:**
- Verificar que el archivo existe en la ruta especificada
- O usar la ruta correcta según el volumen montado

#### **Error 2: HDFS URI incorrecta en queries**

**Ubicación:** `board/hive_connector.py` (líneas 96, 132, 163, 200)

**Problema:**
```python
FROM parquet.`{HDFS_DATA_PATH}`
# Donde HDFS_DATA_PATH = "hdfs://namenode:9000/..."  ❌ INCORRECTO
```

**Análisis:**
- Todas las queries usan `HDFS_DATA_PATH` que está construido con `namenode:9000`
- Debería usar `hdfs://mycluster/...`

---

### 🔴 **CAPA 5: CONFIGURACIÓN DOCKER - ERRORES**

#### **Error 1: DataNodes configurados incorrectamente**

**Ubicación:** `docker/docker-compose.yml` (líneas 289, 324, 356)

**Problema:**
```yaml
- CORE_CONF_fs_defaultFS=hdfs://namenode:9000
```

**Análisis:**
- Los DataNodes están configurados para conectarse a `namenode:9000` directamente
- Pero el cluster está configurado como `hdfs://mycluster` con HA (High Availability)
- Los DataNodes deberían usar `hdfs://mycluster` o la configuración correcta para HA

**Solución:**
- Cambiar a `hdfs://mycluster` o configurar correctamente para HA

#### **Error 2: Spark Consumer usa configuración mixta**

**Ubicación:** `docker/docker-compose.yml` (línea 505)

**Problema:**
- El comando de Spark Consumer tiene configuración hardcodeada para `hdfs://mycluster` ✅
- Pero el código Python en `consumer.py` usa `hdfs://namenode:9000` ❌
- Esto causa conflicto entre la configuración de Spark y el código Python

---

## 🔧 ERRORES ADICIONALES

### **Error 1: Falta archivo .env**

**Problema:**
- El proyecto referencia `.env` pero no existe en el repositorio
- El `start.sh` intenta crear uno desde `.env.example`, pero ese archivo tampoco existe

**Solución:**
- Crear `.env.example` con valores por defecto
- O documentar las variables de entorno necesarias

### **Error 2: Inconsistencia en puertos HDFS**

**Problema:**
- `docker-compose.yml` mapea el puerto 9000 de HDFS a 19000 en el host (línea 138)
- Pero el código usa el puerto 9000 internamente
- Esto puede causar confusión, pero no es un error crítico si se usa correctamente

### **Error 3: Checkpoint location puede causar problemas**

**Ubicación:** `consumer/src/config.py` (línea 33-35)

**Problema:**
```python
CHECKPOINT_LOCATION = os.getenv(
    "SPARK_CHECKPOINT_LOCATION",
    f"hdfs://{HDFS_NAMENODE}:{HDFS_PORT}{HDFS_BASE_PATH}/_checkpoints"
)
```

**Análisis:**
- Usa `hdfs://namenode:9000` en lugar de `hdfs://mycluster`
- Pero en `docker-compose.yml` se usa `/tmp/spark-checkpoints` (línea 501)
- Hay inconsistencia entre la configuración del código y Docker

---

## 📊 RESUMEN DE ERRORES POR PRIORIDAD

### 🔴 **CRÍTICOS (Impiden el funcionamiento):**

1. **Inconsistencia en nombre de cluster HDFS** - Afecta a todas las capas
2. **Configuración incorrecta de DataNodes** - Impide que HDFS funcione correctamente
3. **Consumer usa objeto Config incorrecto** - Puede causar errores en runtime
4. **Dashboard usa HDFS URI incorrecta** - Las queries fallarán

### 🟡 **IMPORTANTES (Causan problemas pero no bloquean todo):**

1. **Falta archivo .env.example** - Puede causar confusión en configuración
2. **Validación de archivos faltante en Producer** - Puede causar errores silenciosos
3. **Inconsistencia en checkpoint location** - Puede causar problemas en reinicios

### 🟢 **MENORES (Mejoras):**

1. **Mensajes de error poco informativos**
2. **Documentación de configuración**

---

## 🎯 SOLUCIÓN RECOMENDADA

### **Opción 1: Usar `hdfs://mycluster` en todo el sistema (RECOMENDADO)**

Ventajas:
- Consistente con la configuración de HA en docker-compose.yml
- Soporta failover automático
- Más robusto

Cambios necesarios:
1. Cambiar `consumer/src/config.py` para usar `hdfs://mycluster`
2. Cambiar `board/hive_connector.py` para usar `hdfs://mycluster`
3. Cambiar `docker/init-hdfs.sh` para usar `hdfs://mycluster`
4. Cambiar DataNodes en `docker-compose.yml` para usar `hdfs://mycluster`
5. Cambiar `spark_query.py` para usar `hdfs://mycluster` por defecto

### **Opción 2: Usar `hdfs://namenode:9000` en todo el sistema**

Ventajas:
- Más simple, sin configuración HA
- Más fácil de entender

Desventajas:
- Requiere cambiar la configuración de HA en docker-compose.yml
- Pierde las ventajas de alta disponibilidad

Cambios necesarios:
1. Cambiar `docker-compose.yml` para usar `hdfs://namenode:9000` en lugar de `hdfs://mycluster`
2. Eliminar configuración de HA
3. Simplificar la configuración de Spark Consumer

---

## 📝 NOTAS ADICIONALES

1. **El código del Consumer usa un patrón anti-pattern** con `type('Config', (), globals())`. Debería refactorizarse para usar imports directos o un objeto Config apropiado.

2. **La configuración de HA (High Availability) de HDFS** está parcialmente implementada pero no se usa correctamente en el código de aplicación.

3. **El dashboard depende de ejecutar comandos Docker** dentro de un contenedor, lo cual puede ser problemático en algunos entornos.

4. **Falta validación de errores** en varios puntos críticos del código.

---

## ✅ CHECKLIST DE CORRECCIONES NECESARIAS

- [ ] Corregir nombre de cluster HDFS en `consumer/src/config.py`
- [ ] Corregir nombre de cluster HDFS en `consumer/src/consumer.py`
- [ ] Corregir nombre de cluster HDFS en `board/hive_connector.py`
- [ ] Corregir nombre de cluster HDFS en `docker/init-hdfs.sh`
- [ ] Corregir configuración de DataNodes en `docker-compose.yml`
- [ ] Corregir default en `spark_query.py` (tanto en `consumer/` como en `board/`)
- [ ] Refactorizar `consumer.py` para no usar `type('Config', (), globals())`
- [ ] Corregir `hdfs_writer.py` para usar correctamente el path
- [ ] Crear archivo `.env.example`
- [ ] Agregar validación de archivos en Producer
- [ ] Unificar configuración de checkpoint location

---

**Fecha de análisis:** $(date)
**Versión del proyecto analizada:** Última versión disponible

