# kafka_reader.py - Lee datos de Kafka usando Spark Structured Streaming

from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, TimestampType

def create_kafka_stream(spark, config):
    """
    Crea un stream de Spark leyendo de Kafka
    
    Args:
        spark: SparkSession
        config: objeto de configuración
    
    Returns:
        DataFrame del stream de Kafka
    """
    # Esquema del JSON que viene del producer
    schema = StructType([
        StructField("datetime", StringType()),
        StructField("global_active_power", DoubleType()),
        StructField("global_reactive_power", DoubleType()),
        StructField("voltage", DoubleType()),
        StructField("global_intensity", DoubleType()),
        StructField("sub_metering_1", DoubleType()),
        StructField("sub_metering_2", DoubleType()),
        StructField("sub_metering_3", DoubleType())
    ])
    
    # Leer stream de Kafka
    df_raw = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", config.KAFKA_BROKER) \
        .option("subscribe", config.KAFKA_TOPIC) \
        .option("startingOffsets", "earliest") \
        .option("failOnDataLoss", "false") \
        .load()
    
    # Convertir el valor binario en texto
    df_parsed = df_raw.selectExpr("CAST(value AS STRING) as json_value")
    
    # Parsear el JSON
    df_data = df_parsed.withColumn("data", from_json(col("json_value"), schema)).select("data.*")
    
    # Convertir datetime a timestamp
    df_final = df_data.withColumn("datetime", col("datetime").cast("timestamp"))
    
    return df_final
