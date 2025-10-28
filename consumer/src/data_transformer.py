# data_transformer.py - Transforma y valida los datos del stream

from pyspark.sql import DataFrame
from pyspark.sql.functions import col, year, month, dayofmonth, hour, when
from pyspark.sql.types import DoubleType

def transform_data(df: DataFrame) -> DataFrame:
    """
    Transforma y valida los datos del stream
    
    Args:
        df: DataFrame con los datos raw de Kafka
    
    Returns:
        DataFrame transformado con campos adicionales
    """
    # Filtrar valores nulos
    df_cleaned = df.na.drop()
    
    # Agregar columnas de particionado para HDFS
    df_partitioned = df_cleaned.withColumn("year", year("datetime")) \
                               .withColumn("month", month("datetime")) \
                               .withColumn("day", dayofmonth("datetime")) \
                               .withColumn("hour", hour("datetime"))
    
    # Validar rangos de valores (opcional, según dominio)
    df_validated = df_partitioned.withColumn(
        "global_active_power",
        when(col("global_active_power") < 0, 0)
        .otherwise(col("global_active_power"))
    ).withColumn(
        "global_reactive_power",
        when(col("global_reactive_power") < 0, 0)
        .otherwise(col("global_reactive_power"))
    )
    
    # Agregar columna de zona (para análisis)
    # Puedes personalizar esto según tus necesidades
    df_with_zones = df_validated.withColumn(
        "zone",
        when(col("sub_metering_1") > col("sub_metering_2"), "zone1")
        .when(col("sub_metering_2") > col("sub_metering_3"), "zone2")
        .otherwise("zone3")
    )
    
    return df_with_zones

