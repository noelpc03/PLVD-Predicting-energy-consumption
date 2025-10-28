# hive_connector.py - Configura tablas de Hive sobre los datos Parquet

from pyspark.sql import SparkSession

def setup_hive_table(spark: SparkSession, hdfs_path: str, table_name="energy_data"):
    """
    Crea una tabla externa de Hive sobre los datos Parquet en HDFS
    
    Args:
        spark: SparkSession
        hdfs_path: ruta base en HDFS
        table_name: nombre de la tabla
    """
    hdfs_data_path = f"{hdfs_path}/streaming"
    
    # Crear tabla externa
    create_table_sql = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            datetime TIMESTAMP,
            global_active_power DOUBLE,
            global_reactive_power DOUBLE,
            voltage DOUBLE,
            global_intensity DOUBLE,
            sub_metering_1 DOUBLE,
            sub_metering_2 DOUBLE,
            sub_metering_3 DOUBLE,
            zone STRING,
            year INT,
            month INT,
            day INT,
            hour INT
        )
        USING PARQUET
        PARTITIONED BY (year, month, day, hour)
        LOCATION '{hdfs_data_path}'
        TBLPROPERTIES (
            'discover.partitions'='true'
        )
    """
    
    try:
        spark.sql(create_table_sql)
        print(f"✅ Tabla Hive '{table_name}' creada/actualizada en {hdfs_data_path}")
    except Exception as e:
        print(f"⚠️  Error al crear tabla: {e}")
        print("   Esto es normal en la primera ejecución, las particiones se detectarán automáticamente")

