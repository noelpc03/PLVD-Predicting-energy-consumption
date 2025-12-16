#!/usr/bin/env python3
"""Script para verificar conexión con Hive Metastore"""
from pyspark.sql import SparkSession
import sys

print("=" * 80)
print("🔍 VERIFICANDO HIVE METASTORE")
print("=" * 80)

try:
    # Crear Spark Session con soporte para Hive
    print("\n1️⃣ Creando Spark Session con Hive support...")
    spark = SparkSession.builder \
        .appName("MetastoreTest") \
        .config("spark.sql.warehouse.dir", "hdfs://namenode:9000/user/hive/warehouse") \
        .config("spark.hadoop.fs.defaultFS", "hdfs://namenode:9000") \
        .config("hive.metastore.uris", "thrift://hive-metastore:9083") \
        .enableHiveSupport() \
        .getOrCreate()
    
    spark.sparkContext.setLogLevel("ERROR")
    print("✅ Spark Session creada")
    
    # Verificar conexión intentando listar tablas
    print("\n2️⃣ Verificando conexión al Metastore (listando tablas)...")
    try:
        tables = spark.sql("SHOW TABLES").collect()
        print(f"✅ Conexión exitosa! Tablas encontradas: {len(tables)}")
        
        if tables:
            print("\n📋 Tablas registradas:")
            for table in tables:
                table_name = table['tableName'] if 'tableName' in table else table[1]
                database = table['database'] if 'database' in table else table[0]
                print(f"   - {database}.{table_name}")
        else:
            print("   (No hay tablas registradas aún)")
            
    except Exception as e:
        print(f"⚠️  Error al listar tablas: {e}")
        print("   Esto puede ser normal si es la primera vez")
    
    # Verificar si existe la tabla energy_data
    print("\n3️⃣ Verificando si existe la tabla 'energy_data'...")
    try:
        result = spark.sql("SHOW TABLES LIKE 'energy_data'").collect()
        if result:
            print("✅ Tabla 'energy_data' encontrada!")
            
            # Obtener detalles de la tabla
            print("\n4️⃣ Obteniendo detalles de la tabla...")
            desc = spark.sql("DESCRIBE EXTENDED energy_data").collect()
            print("   Columnas y propiedades:")
            for row in desc[:15]:  # Mostrar primeras 15 líneas
                print(f"   {row}")
        else:
            print("⚠️  Tabla 'energy_data' no encontrada en el Metastore")
            print("   Esto puede significar que el consumer no la ha creado aún")
            
    except Exception as e:
        print(f"⚠️  Error al verificar tabla: {e}")
    
    # Verificar que puede acceder a los datos en HDFS directamente
    print("\n5️⃣ Verificando acceso a datos en HDFS...")
    try:
        hdfs_path = "hdfs://namenode:9000/user/amalia/energy_data/streaming"
        df = spark.read.parquet(hdfs_path)
        count = df.count()
        print(f"✅ Acceso a HDFS OK! Registros encontrados: {count:,}")
    except Exception as e:
        print(f"❌ Error al acceder a HDFS: {e}")
    
    print("\n" + "=" * 80)
    print("✅ Verificación completada")
    print("=" * 80)
    
    spark.stop()
    
except Exception as e:
    print(f"\n❌ Error general: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

