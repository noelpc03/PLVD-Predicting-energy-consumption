#!/usr/bin/env python3
"""Script para probar consultas SQL usando la tabla registrada en Hive"""
from pyspark.sql import SparkSession

print("=" * 80)
print("🧪 PROBANDO CONSULTAS SQL CON LA TABLA REGISTRADA")
print("=" * 80)

spark = SparkSession.builder \
    .appName("TableQueryTest") \
    .config("spark.sql.warehouse.dir", "hdfs://namenode:9000/user/hive/warehouse") \
    .config("spark.hadoop.fs.defaultFS", "hdfs://namenode:9000") \
    .config("hive.metastore.uris", "thrift://hive-metastore:9083") \
    .enableHiveSupport() \
    .getOrCreate()

spark.sparkContext.setLogLevel("ERROR")

try:
    print("\n1️⃣ Consulta simple: Contar registros")
    count = spark.sql("SELECT COUNT(*) as total FROM energy_data").collect()[0]['total']
    print(f"   ✅ Total: {count:,} registros")
    
    print("\n2️⃣ Consulta con WHERE: Registros del año 2006")
    count_2006 = spark.sql("SELECT COUNT(*) as total FROM energy_data WHERE year = 2006").collect()[0]['total']
    print(f"   ✅ Año 2006: {count_2006:,} registros")
    
    print("\n3️⃣ Consulta con GROUP BY: Registros por zona")
    zones = spark.sql("SELECT zone, COUNT(*) as cantidad FROM energy_data GROUP BY zone ORDER BY cantidad DESC").collect()
    print("   ✅ Resultados:")
    for row in zones:
        print(f"      - {row['zone']}: {row['cantidad']:,} registros")
    
    print("\n4️⃣ Consulta con agregaciones: Estadísticas por año")
    stats = spark.sql("""
        SELECT 
            year,
            COUNT(*) as total_registros,
            ROUND(AVG(global_active_power), 2) as promedio_potencia,
            ROUND(MAX(global_active_power), 2) as max_potencia
        FROM energy_data 
        GROUP BY year 
        ORDER BY year
    """).collect()
    print("   ✅ Resultados:")
    for row in stats:
        print(f"      Año {row['year']}: {row['total_registros']:,} registros, "
              f"Promedio: {row['promedio_potencia']} kW, "
              f"Máximo: {row['max_potencia']} kW")
    
    print("\n5️⃣ Consulta con particiones: Verificar particionado")
    partitions = spark.sql("SELECT DISTINCT year, month FROM energy_data ORDER BY year, month LIMIT 5").collect()
    print("   ✅ Particiones (primeras 5):")
    for row in partitions:
        print(f"      - Año {row['year']}, Mes {row['month']}")
    
    print("\n" + "=" * 80)
    print("✅ ¡TODAS LAS CONSULTAS FUNCIONARON CORRECTAMENTE!")
    print("=" * 80)
    print("\n📊 La tabla 'energy_data' está:")
    print("   ✅ Registrada en Hive Metastore")
    print("   ✅ Accesible vía SQL")
    print("   ✅ Los datos están en HDFS")
    print("   ✅ Las particiones funcionan correctamente")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

spark.stop()

