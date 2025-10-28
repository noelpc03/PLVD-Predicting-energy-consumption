# consumer.py - Consumer principal que integra todos los módulos

from pyspark.sql import SparkSession
import sys
import os

# Agregar el directorio src al path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from config import *
from kafka_reader import create_kafka_stream
from data_transformer import transform_data
from hdfs_writer import write_to_hdfs
from hive_connector import setup_hive_table

def main():
    """
    Función principal del Consumer
    Lee datos de Kafka, los transforma y escribe en HDFS
    """
    
    # Crear Spark Session con soporte para Kafka, Hive y HDFS
    spark = SparkSession.builder \
        .appName("EnergyDataConsumer") \
        .config("spark.sql.warehouse.dir", f"hdfs://{HDFS_NAMENODE}:{HDFS_PORT}/user/hive/warehouse") \
        .config("spark.hadoop.fs.defaultFS", f"hdfs://{HDFS_NAMENODE}:{HDFS_PORT}") \
        .config("spark.sql.streaming.checkpointLocation", CHECKPOINT_LOCATION) \
        .enableHiveSupport() \
        .getOrCreate()
    
    spark.sparkContext.setLogLevel("WARN")
    
    print("🚀 Iniciando Consumer de datos energéticos...")
    print(f"📡 Broker Kafka: {KAFKA_BROKER}")
    print(f"📨 Topic: {KAFKA_TOPIC}")
    print(f"💾 HDFS: hdfs://{HDFS_NAMENODE}:{HDFS_PORT}")
    
    try:
        # Configurar tabla de Hive (una sola vez al inicio)
        print("🗃️  Configurando tablas de Hive...")
        setup_hive_table(spark, HDFS_PATH)
        
        # 1. Leer stream de Kafka
        print("\n📖 Leyendo stream de Kafka...")
        df_stream = create_kafka_stream(spark, type('Config', (), globals()))
        
        # 2. Transformar datos
        print("🔄 Transformando datos...")
        df_transformed = transform_data(df_stream)
        
        # 3. Escribir en HDFS
        print("💾 Escribiendo en HDFS...")
        query = write_to_hdfs(df_transformed, type('Config', (), globals()), CHECKPOINT_LOCATION)
        
        print("\n✅ Consumer iniciado correctamente")
        print("📊 Procesando stream continuamente...")
        print("🛑 Presiona Ctrl+C para detener")
        
        # Esperar terminación
        query.awaitTermination()
        
    except KeyboardInterrupt:
        print("\n⏹️  Deteniendo consumer...")
        query.stop()
        spark.stop()
        print("✅ Consumer detenido correctamente")
    except Exception as e:
        print(f"❌ Error en consumer: {e}")
        raise

if __name__ == "__main__":
    main()

