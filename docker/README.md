# 🚀 Instrucciones de Uso - Sistema de Procesamiento de Datos Energéticos

## 📋 Requisitos Previos

1. **Docker y Docker Compose** instalados
2. **Dataset** ubicado en `../data/dataset.txt`
3. **Memoria suficiente**: al menos 8GB RAM recomendados

## 🏃 Inicio Rápido

### 1. Levantar el Sistema Completo

```bash
cd docker
docker compose up -d
```

Esto iniciará todos los servicios:
- **Zookeeper** (puerto 2181)
- **Kafka** (puerto 9092)
- **HDFS Namenode** (puerto 9870)
- **HDFS Datanode** (puerto 9864)
- **Yarn Resource Manager** (puerto 8088)
- **Yarn Node Manager** (puerto 8042)
- **Hive Metastore** (puerto 9083)
- **Producer** (enviando datos)
- **Spark Consumer** (procesando y guardando en HDFS)

### 2. Verificar Que Todo Está Funcionando

```bash
# Ver logs del producer
docker logs producer

# Ver logs del consumer
docker logs spark-consumer

# Ver logs de Kafka
docker logs kafka

# Ver logs de HDFS
docker logs namenode
docker logs datanode
```

### 3. Acceder a las Interfaces Web

- **Spark UI**: http://localhost:4040
- **Yarn Resource Manager**: http://localhost:8088
- **HDFS Namenode**: http://localhost:9870
- **Kafka**: http://localhost:9092

### 4. Verificar Datos en HDFS

```bash
# Acceder al contenedor de namenode
docker exec -it namenode bash

# Listar directorios en HDFS
hdfs dfs -ls /user/amalia/energy_data/

# Ver archivos Parquet
hdfs dfs -ls /user/amalia/energy_data/streaming/

# Contar registros
hdfs dfs -count /user/amalia/energy_data/streaming/
```

### 5. Consultar Datos con Hive

```bash
# Acceder al contenedor de spark-consumer
docker exec -it spark-consumer bash

# Iniciar Spark SQL
/opt/spark/bin/spark-sql

# Consultar datos
SELECT * FROM energy_data LIMIT 10;
SELECT zone, COUNT(*) FROM energy_data GROUP BY zone;
SELECT year, month, COUNT(*) FROM energy_data GROUP BY year, month;
```

## 🛑 Detener el Sistema

```bash
# Detener todos los contenedores
docker compose down

# Detener y eliminar volúmenes (⚠️ elimina datos)
docker compose down -v
```

## 🔧 Solución de Problemas

### Producer no envía datos

```bash
# Ver logs detallados
docker logs -f producer

# Verificar que Kafka está listo
docker exec -it kafka kafka-topics --list --bootstrap-server localhost:9092
```

### Consumer no procesa

```bash
# Ver logs
docker logs -f spark-consumer

# Reiniciar consumer
docker compose restart spark-consumer
```

### HDFS sin conexión

```bash
# Verificar que namenode está activo
docker logs namenode

# Verificar formato de disco
docker exec -it namenode hdfs namenode -format
```

## 📊 Monitoreo

### Ver Estadísticas de Kafka

```bash
docker exec -it kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic energy_stream \
  --from-beginning
```

### Ver Uso de Recursos

```bash
docker stats
```

## 📝 Estructura de Datos

Los datos se almacenan en HDFS con la siguiente estructura:

```
/user/amalia/energy_data/streaming/
  └── year=2024/
      └── month=01/
          └── day=15/
              └── hour=10/
                  └── part-00000.parquet
```

### Formato de los Datos

Cada mensaje JSON contiene:
- `datetime`: timestamp de la medición
- `global_active_power`: potencia activa global
- `global_reactive_power`: potencia reactiva global
- `voltage`: voltaje
- `global_intensity`: intensidad de corriente
- `sub_metering_1`, `sub_metering_2`, `sub_metering_3`: consumo por zona
- `zone`: zona con mayor consumo

## 🎯 Próximos Pasos

1. **Dashboard**: Implementar visualización en tiempo real
2. **Predicciones**: Modelo de ML para predecir consumo futuro
3. **Alertas**: Sistema de notificaciones para picos de consumo

