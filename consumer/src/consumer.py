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
        .appName(SPARK_APP_NAME) \
        .config("spark.sql.warehouse.dir", f"hdfs://{HDFS_NAMENODE}:{HDFS_PORT}/user/hive/warehouse") \
        .config("spark.hadoop.fs.defaultFS", f"hdfs://{HDFS_NAMENODE}:{HDFS_PORT}") \
        .config("spark.sql.streaming.checkpointLocation", CHECKPOINT_LOCATION) \
        .config("hive.metastore.uris", HIVE_METASTORE_URI) \
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
        setup_hive_table(spark, HDFS_PATH, HIVE_TABLE_NAME)
        
        # 1. Leer stream de Kafka
        print("\n📖 Leyendo stream de Kafka...")
        df_stream = create_kafka_stream(spark, type('Config', (), globals()))
        
        # 2. Transformar datos
        print("🔄 Transformando datos...")
        df_transformed = transform_data(df_stream)
        
        # 2.5. Función para mostrar mensajes y escribir a HDFS
        hdfs_output_path = f"{HDFS_PATH}/streaming"
        def show_and_write(batch_df, batch_id):
            """Callback para mostrar mensajes y escribir a HDFS"""
            count = batch_df.count()
            print(f"\n📊 Batch {batch_id}: Procesando {count} mensajes")
            print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            if count > 0:
                batch_df.show(n=20, truncate=False)  # Mostrar hasta 20 filas
                if count > 20:
                    print(f"... y {count - 20} mensajes más")
            print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
            # Escribir a HDFS
            batch_df.write \
                .mode("append") \
                .format("parquet") \
                .partitionBy("year", "month", "day", "hour") \
                .save(hdfs_output_path)
        
        # 3. Escribir en HDFS con callback para mostrar mensajes
        print("💾 Escribiendo en HDFS (y mostrando mensajes en logs)...")
        processing_interval = f"{SPARK_PROCESSING_INTERVAL} seconds"
        
        query = df_transformed.writeStream \
            .outputMode("append") \
            .foreachBatch(show_and_write) \
            .option("checkpointLocation", CHECKPOINT_LOCATION) \
            .trigger(processingTime=processing_interval) \
            .start()
        
        print("\n✅ Consumer iniciado correctamente")
        print("📊 Procesando stream continuamente...")
        print("📺 Los mensajes se mostrarán en los logs cada batch...")
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

