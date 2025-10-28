# ⚡ PLVD - Predicting Energy Consumption

## 📋 Descripción

Sistema de procesamiento de grandes volúmenes de datos para predecir la demanda eléctrica en tiempo real, utilizando el ecosistema **Hadoop** y **Apache Spark**.

Este proyecto implementa una arquitectura completa de streaming que incluye:
- **Kafka** como sistema de mensajería
- **HDFS** para almacenamiento distribuido
- **Spark Structured Streaming** para procesamiento en tiempo real
- **Hive** para consultas SQL sobre datos históricos

## 🏗️ Arquitectura

```
Dataset → Producer (Python) → Kafka → Consumer (Spark) → HDFS (Parquet) → Hive → Dashboard
```

## 🚀 Inicio Rápido

```bash
# 1. Ir al directorio docker
cd docker

# 2. Inicializar HDFS
./init-hdfs.sh

# 3. Levantar el sistema completo
docker compose up -d

# 4. Ver logs
docker logs -f producer
docker logs -f spark-consumer
```

## 📁 Estructura del Proyecto

```
PLVD-Predicting-energy-consumption/
├── producer/          # Productor de datos (envía a Kafka)
│   ├── config.py
│   ├── data_loader.py
│   ├── kafka_client.py
│   ├── message_builder.py
│   └── producer.py
├── consumer/          # Consumidor de datos (Spark)
│   └── src/
│       ├── config.py
│       ├── consumer.py
│       ├── kafka_reader.py
│       ├── data_transformer.py
│       ├── hdfs_writer.py
│       └── hive_connector.py
├── docker/            # Configuración Docker
│   ├── docker-compose.yml
│   ├── init-hdfs.sh
│   └── README.md
└── data/             # Dataset energético
    └── dataset.txt
```

## 🔧 Tecnologías Utilizadas

- **Hadoop HDFS**: Almacenamiento distribuido
- **Apache Kafka**: Mensajería en tiempo real
- **Apache Spark**: Procesamiento distribuido
- **Apache Hive**: Consultas SQL sobre datos
- **Docker**: Contenedorización
- **Python**: Lenguaje de programación

## 📊 Características

### Datos Procesados
- Potencia activa y reactiva global
- Voltaje e intensidad de corriente
- Consumo por zonas (Sub_metering_1/2/3)
- Timestamps con granularidad por hora

### Funcionalidades
- ✅ Streaming de datos en tiempo real
- ✅ Almacenamiento en HDFS formato Parquet
- ✅ Particionado por año, mes, día y hora
- ✅ Consultas SQL con Hive
- ✅ Procesamiento exactly-once
- ✅ Escalable y tolerante a fallos

## 📖 Documentación

Ver [docker/README.md](docker/README.md) para instrucciones detalladas de uso.

## 🔗 Dataset

**Household Electric Power Consumption Dataset**
- Fuente: https://www.kaggle.com/datasets/uciml/electric-power-consumption-data-set
- 2+ millones de registros
- Mediciones minuto a minuto (2006-2010)
- Tamaño: ~120 MB

## 🎯 Objetivos

- Predecir el consumo energético en las próximas horas
- Detectar patrones de demanda
- Visualizar datos en tiempo real
- Analizar impacto del clima en el consumo
- Generar alertas por picos de demanda

## 👥 Autores

- Amalia Beatriz Valiente Hinojosa
- Noel Pérez Calvo

