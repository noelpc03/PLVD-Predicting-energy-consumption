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

---

## 🚀 Inicio Rápido (3 Pasos)

### **Paso 0: Configuración (Opcional)**
El proyecto incluye un archivo `.env.example` con todas las variables de entorno configurables.
Si necesitas personalizar la configuración:

```bash
# Copiar el archivo de ejemplo
cp .env.example .env

# Editar con tus valores personalizados (opcional)
# Los valores por defecto funcionan con la configuración estándar
```

**Nota:** El archivo `.env` está en `.gitignore` y no se subirá al repositorio. 
El archivo `.env.example` contiene valores por defecto que funcionan con la configuración estándar.

### **Paso 1: Verificar Requisitos**
```bash
./check-requirements.sh
```

### **Paso 2: Iniciar el Sistema**
```bash
./start.sh
```

### **Paso 3: Monitorear**
```bash
# Ver logs del Producer
docker logs -f producer

# Ver logs del Consumer
docker logs -f spark-consumer

# Interfaces Web:
# HDFS:     http://localhost:9870
# Spark:    http://localhost:4040
# Dashboard: http://localhost:5001
```

---

## 📖 Documentación Completa

Si no tienes Docker instalado o es tu primera vez:
- 📄 **[INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md)** - Guía completa de instalación desde cero
- 📄 **[CONFIGURATION.md](CONFIGURATION.md)** - Configuración mediante variables de entorno
- 📄 **[docker/FIXES_APPLIED.md](docker/FIXES_APPLIED.md)** - Correcciones aplicadas al sistema

---

## 🛑 Detener el Sistema

```bash
cd docker
docker compose down
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
- ✅ Configuración flexible mediante variables de entorno
- ✅ **Dashboard web moderno** con visualización en tiempo real
- ✅ Gráficos interactivos y métricas en vivo

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

