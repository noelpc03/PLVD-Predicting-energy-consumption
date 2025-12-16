#!/usr/bin/env python3
"""Script temporal para consultar datos de HDFS"""
from pyspark.sql import SparkSession

# Crear Spark Session
spark = SparkSession.builder \
    .appName("QueryHDFS") \
    .config("spark.sql.warehouse.dir", "hdfs://namenode:9000/user/hive/warehouse") \
    .config("spark.hadoop.fs.defaultFS", "hdfs://namenode:9000") \
    .enableHiveSupport() \
    .getOrCreate()

spark.sparkContext.setLogLevel("ERROR")

print("=" * 80)
print("📊 CONSULTANDO DATOS DE HDFS")
print("=" * 80)

# Contar registros totales
print("\n1️⃣ Total de registros guardados:")
count = spark.sql("SELECT COUNT(*) as total FROM energy_data").collect()[0]['total']
print(f"   Total: {count:,} registros")

# Mostrar algunos registros de ejemplo
print("\n2️⃣ Primeros 10 registros:")
spark.sql("SELECT * FROM energy_data ORDER BY datetime LIMIT 10").show(truncate=False)

# Estadísticas por año
print("\n3️⃣ Registros por año:")
spark.sql("SELECT year, COUNT(*) as cantidad FROM energy_data GROUP BY year ORDER BY year").show()

# Promedio de consumo por año
print("\n4️⃣ Consumo promedio (global_active_power) por año:")
spark.sql("""
    SELECT 
        year, 
        ROUND(AVG(global_active_power), 2) as promedio_potencia,
        ROUND(MAX(global_active_power), 2) as max_potencia,
        ROUND(MIN(global_active_power), 2) as min_potencia
    FROM energy_data 
    GROUP BY year 
    ORDER BY year
""").show(truncate=False)

# Registros por zona
print("\n5️⃣ Registros por zona:")
spark.sql("SELECT zone, COUNT(*) as cantidad FROM energy_data GROUP BY zone ORDER BY cantidad DESC").show()

print("\n" + "=" * 80)
print("✅ Consulta completada")
print("=" * 80)

spark.stop()

