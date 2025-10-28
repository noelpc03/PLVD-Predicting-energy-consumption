# hdfs_writer.py - Escribe datos en HDFS en formato Parquet

from pyspark.sql import DataFrame
from pyspark.sql import SparkSession

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
    
    # Escribir en HDFS con particionado
    query = df.writeStream \
        .outputMode("append") \
        .format("parquet") \
        .option("path", hdfs_output_path) \
        .option("checkpointLocation", checkpoint_location) \
        .partitionBy("year", "month", "day", "hour") \
        .trigger(processingTime='60 seconds') \
        .start()
    
    return query

