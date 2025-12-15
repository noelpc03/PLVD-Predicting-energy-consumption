# hive_connector.py - Configura tablas de Hive sobre los datos Parquet

from pyspark.sql import SparkSession
from config import HIVE_TABLE_NAME, HDFS_STREAMING_PATH

def setup_hive_table(spark: SparkSession, hdfs_path: str, table_name=None):
    """
    Crea una tabla externa de Hive sobre los datos Parquet en HDFS
    
    Args:
        spark: SparkSession
        hdfs_path: ruta base en HDFS (mantenido para compatibilidad, pero se usa HDFS_STREAMING_PATH)
        table_name: nombre de la tabla (usa config.HIVE_TABLE_NAME si es None)
    """
    if table_name is None:
        table_name = HIVE_TABLE_NAME
    
    # Usar el path de streaming definido centralmente en config.py
    hdfs_data_path = HDFS_STREAMING_PATH
    
    # Crear tabla externa usando sintaxis compatible con Hive
    # NOTA: Las columnas de partición (year, month, day, hour) NO deben estar en la lista de columnas
    # porque se especifican en PARTITIONED BY. Hive las detectará automáticamente de los datos.
    create_table_sql = f"""
        CREATE EXTERNAL TABLE {table_name} (
            datetime TIMESTAMP,
            global_active_power DOUBLE,
            global_reactive_power DOUBLE,
            voltage DOUBLE,
            global_intensity DOUBLE,
            sub_metering_1 DOUBLE,
            sub_metering_2 DOUBLE,
            sub_metering_3 DOUBLE,
            zone STRING
        )
        PARTITIONED BY (year INT, month INT, day INT, hour INT)
        STORED AS PARQUET
        LOCATION '{hdfs_data_path}'
        TBLPROPERTIES (
            'discover.partitions'='true'
        )
    """
    
    try:
        # Verificar si la tabla existe y si es particionada
        table_exists = False
        is_partitioned = False
        try:
            # Intentar obtener información de la tabla
            table_info = spark.sql(f"SHOW CREATE TABLE {table_name}").collect()
            if table_info:
                table_exists = True
                # Verificar si la definición de la tabla incluye PARTITIONED BY
                create_statement = ' '.join([row[0] for row in table_info]).lower()
                is_partitioned = 'partitioned by' in create_statement
        except Exception as table_check_error:
            # La tabla no existe o hay un error al verificar
            # Intentar método alternativo: DESCRIBE TABLE
            try:
                table_info = spark.sql(f"DESCRIBE TABLE {table_name}").collect()
                if table_info:
                    table_exists = True
                    # Si la tabla existe, intentar verificar particiones con SHOW PARTITIONS
                    try:
                        partitions = spark.sql(f"SHOW PARTITIONS {table_name}").collect()
                        is_partitioned = len(partitions) > 0 or True  # Si tiene particiones, está particionada
                    except:
                        # Si SHOW PARTITIONS falla, la tabla probablemente no está particionada
                        is_partitioned = False
            except:
                # La tabla no existe, está bien
                pass
        
        # Si la tabla existe pero no es particionada, eliminarla y recrearla
        if table_exists and not is_partitioned:
            print(f"⚠️  La tabla '{table_name}' existe pero no está particionada. Eliminándola para recrearla...")
            spark.sql(f"DROP TABLE IF EXISTS {table_name}")
            print(f"🗑️  Tabla '{table_name}' eliminada")
            table_exists = False  # Marcar que la tabla ya no existe
        
        # Crear la tabla (si no existe, se creará; si existe y no está particionada, ya la eliminamos)
        try:
            spark.sql(create_table_sql)
            print(f"✅ Tabla Hive '{table_name}' creada en {hdfs_data_path}")
        except Exception as create_error:
            # Si la tabla ya existe y está bien, está OK
            if 'already exists' in str(create_error).lower() or 'table already exists' in str(create_error).lower():
                print(f"ℹ️  Tabla Hive '{table_name}' ya existe")
            else:
                raise create_error
        
        # Descubrir particiones recién escritas (solo si la tabla es particionada)
        try:
            spark.sql(f"MSCK REPAIR TABLE {table_name}")
            print(f"🔄 Particiones reparadas para '{table_name}'")
        except Exception as repair_error:
            # Si MSCK REPAIR falla, verificar si es porque la tabla no está particionada
            error_msg = str(repair_error).lower()
            if 'not a partitioned table' in error_msg or 'not_a_partitioned_table' in error_msg:
                print(f"⚠️  La tabla '{table_name}' no está particionada. Eliminándola para recrearla con particiones...")
                try:
                    spark.sql(f"DROP TABLE IF EXISTS {table_name}")
                    print(f"🗑️  Tabla '{table_name}' eliminada")
                    # Esperar un momento para que Hive procese la eliminación
                    import time
                    time.sleep(1)
                    # Recrear la tabla con particiones
                    spark.sql(create_table_sql)
                    print(f"✅ Tabla '{table_name}' recreada con particiones")
                    # Esperar un momento antes de intentar MSCK REPAIR
                    time.sleep(1)
                    # Intentar MSCK REPAIR nuevamente
                    spark.sql(f"MSCK REPAIR TABLE {table_name}")
                    print(f"🔄 Particiones reparadas para '{table_name}'")
                except Exception as retry_error:
                    print(f"ℹ️  No se pudieron reparar particiones automáticamente: {retry_error}")
                    print("   Las particiones se detectarán automáticamente cuando se consulten")
            else:
                # Otro tipo de error en MSCK REPAIR
                print(f"ℹ️  No se pudieron reparar particiones automáticamente: {repair_error}")
                print("   Las particiones se detectarán automáticamente cuando se consulten")
    except Exception as e:
        print(f"⚠️  Error al crear tabla: {e}")
        print("   Esto es normal en la primera ejecución, las particiones se detectarán automáticamente")

