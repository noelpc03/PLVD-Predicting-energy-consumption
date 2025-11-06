# hdfs_writer.py - Escribe datos en HDFS en formato Parquet

from pyspark.sql import DataFrame
from pyspark.sql import SparkSession
from config import HDFS_PATH, SPARK_PROCESSING_INTERVAL

def write_to_hdfs(df: DataFrame, config, checkpoint_location: str):
    """
    Escribe el stream de datos a HDFS en formato Parquet
    
    Args:
        df: DataFrame transformado
        config: objeto de configuración
        checkpoint_location: ubicación de los checkpoints
    
    Returns:
        StreamingQuery object
    """
    # Path de HDFS para escribir los datos
    hdfs_output_path = f"{config.HDFS_PATH}/streaming"
    
    # Intervalo de procesamiento desde configuración
    processing_interval = f"{SPARK_PROCESSING_INTERVAL} seconds"
    
    # Escribir en HDFS con particionado
    query = df.writeStream \
        .outputMode("append") \
        .format("parquet") \
        .option("path", hdfs_output_path) \
        .option("checkpointLocation", checkpoint_location) \
        .partitionBy("year", "month", "day", "hour") \
        .trigger(processingTime=processing_interval) \
        .start()
    
    return query

