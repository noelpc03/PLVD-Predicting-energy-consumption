#!/usr/bin/env python3
"""Script para consultar datos de HDFS directamente desde Parquet"""
from pyspark.sql import SparkSession

# Crear Spark Session (sin Hive)
spark = SparkSession.builder \
    .appName("QueryHDFS") \
    .config("spark.hadoop.fs.defaultFS", "hdfs://namenode:9000") \
    .getOrCreate()

spark.sparkContext.setLogLevel("ERROR")

print("=" * 80)
print("📊 CONSULTANDO DATOS DE HDFS (lectura directa Parquet)")
print("=" * 80)

# Leer directamente desde Parquet
hdfs_path = "hdfs://namenode:9000/user/amalia/energy_data/streaming"
df = spark.read.parquet(hdfs_path)

# Contar registros totales
print("\n1️⃣ Total de registros guardados:")
count = df.count()
print(f"   Total: {count:,} registros")

# Mostrar algunos registros de ejemplo
print("\n2️⃣ Primeros 10 registros:")
df.orderBy("datetime").show(10, truncate=False)

# Estadísticas por año
print("\n3️⃣ Registros por año:")
df.groupBy("year").count().orderBy("year").show()

# Promedio de consumo por año
print("\n4️⃣ Consumo promedio (global_active_power) por año:")
from pyspark.sql.functions import avg, max, min, round
df.groupBy("year").agg(
    round(avg("global_active_power"), 2).alias("promedio_potencia"),
    round(max("global_active_power"), 2).alias("max_potencia"),
    round(min("global_active_power"), 2).alias("min_potencia")
).orderBy("year").show(truncate=False)

# Registros por zona
print("\n5️⃣ Registros por zona:")
df.groupBy("zone").count().orderBy("count", ascending=False).show()

print("\n" + "=" * 80)
print("✅ Consulta completada")
print("=" * 80)

spark.stop()

