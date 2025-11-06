# hive_connector.py - Conector para leer datos Parquet desde HDFS usando Spark SQL
import os
import subprocess
import json
import pandas as pd
from typing import Optional, List, Dict

# Cargar variables de entorno
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

HDFS_NAMENODE = os.getenv("HDFS_NAMENODE", "namenode")
HDFS_PORT = int(os.getenv("HDFS_PORT", "9000"))
HDFS_USER = os.getenv("HDFS_USER", "amalia")
PROJECT_NAME = os.getenv("PROJECT_NAME", "energy_data")
HIVE_TABLE_NAME = os.getenv("HIVE_TABLE_NAME", "energy_data")

# Path de datos en HDFS
HDFS_DATA_PATH = f"hdfs://{HDFS_NAMENODE}:{HDFS_PORT}/user/{HDFS_USER}/{PROJECT_NAME}/streaming"

def execute_spark_sql(query: str) -> pd.DataFrame:
    """Ejecuta una query SQL usando PySpark en el contenedor spark-consumer"""
    try:
        # Ejecutar script Python usando spark-submit dentro del contenedor de Spark
        hdfs_uri = f"hdfs://{HDFS_NAMENODE}:{HDFS_PORT}"
        cmd = [
            'docker', 'exec', 'spark-consumer',
            '/opt/spark/bin/spark-submit',
            '--master', 'local[1]',
            '--driver-memory', '512m',  # Reducir memoria del driver
            '--executor-memory', '512m',  # Reducir memoria del executor
            '--conf', f'spark.hadoop.fs.defaultFS={hdfs_uri}',
            '--conf', 'spark.driver.maxResultSize=256m',  # Limitar tamaño de resultados
            '/app/consumer/spark_query.py',
            query,
            hdfs_uri
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120  # Aumentar timeout a 2 minutos para queries grandes
        )
        
        if result.returncode != 0:
            error_msg = result.stderr or result.stdout
            print(f"Error ejecutando Spark SQL: {error_msg[:500]}")
            return pd.DataFrame()
        
        # Parsear JSON output
        output = result.stdout.strip()
        if not output:
            return pd.DataFrame()
        
        try:
            data = json.loads(output)
            if isinstance(data, dict) and 'error' in data:
                print(f"Error en query: {data['error']}")
                return pd.DataFrame()
            if isinstance(data, list) and len(data) > 0:
                df = pd.DataFrame(data)
            else:
                df = pd.DataFrame()
            return df
        except json.JSONDecodeError as e:
            print(f"Error parseando JSON: {e}")
            print(f"Output: {output[:200]}")
            return pd.DataFrame()
        
    except subprocess.TimeoutExpired:
        print("Timeout ejecutando query Spark SQL")
        return pd.DataFrame()
    except Exception as e:
        print(f"Error ejecutando Spark SQL: {e}")
        import traceback
        traceback.print_exc()
        return pd.DataFrame()

def execute_query_python(query_func):
    """Ejecuta una función que genera una query SQL y la ejecuta"""
    try:
        query = query_func()
        return execute_spark_sql(query)
    except Exception as e:
        print(f"Error en query: {e}")
        return pd.DataFrame()

def get_latest_data(limit: int = 100) -> List[Dict]:
    """Obtiene los últimos N registros"""
    def query_func():
        # Leer directamente desde Parquet sin usar tabla Hive
        return f"""
            SELECT 
                datetime,
                global_active_power,
                global_reactive_power,
                voltage,
                global_intensity,
                sub_metering_1,
                sub_metering_2,
                sub_metering_3
            FROM parquet.`{HDFS_DATA_PATH}`
            ORDER BY datetime DESC
            LIMIT {limit}
        """
    
    df = execute_query_python(query_func)
    
    if df.empty:
        return []
    
    # Convertir tipos numéricos
    numeric_cols = ['global_active_power', 'global_reactive_power', 'voltage', 
                    'global_intensity', 'sub_metering_1', 'sub_metering_2', 'sub_metering_3']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Convertir a lista de diccionarios
    if 'datetime' in df.columns:
        df['datetime'] = pd.to_datetime(df['datetime'], errors='coerce').dt.strftime('%Y-%m-%d %H:%M:%S')
    return df.to_dict('records')

def get_statistics() -> Dict:
    """Obtiene estadísticas agregadas"""
    def query_func():
        # Leer directamente desde Parquet sin usar tabla Hive
        return f"""
            SELECT 
                COUNT(*) as total_records,
                AVG(global_active_power) as avg_active_power,
                MAX(global_active_power) as max_active_power,
                MIN(global_active_power) as min_active_power,
                AVG(voltage) as avg_voltage,
                AVG(global_intensity) as avg_intensity,
                SUM(sub_metering_1 + sub_metering_2 + sub_metering_3) as total_sub_metering
            FROM parquet.`{HDFS_DATA_PATH}`
        """
    
    df = execute_query_python(query_func)
    
    if df.empty:
        return {}
    
    result = df.iloc[0].to_dict()
    # Convertir valores numéricos
    for key, value in result.items():
        if isinstance(value, str):
            try:
                result[key] = float(value)
            except:
                pass
    return result

def get_time_series_data(hours: int = 24) -> List[Dict]:
    """Obtiene datos de series de tiempo agregados por datetime"""
    def query_func():
        # Leer directamente desde Parquet sin usar tabla Hive
        return f"""
            SELECT 
                datetime,
                AVG(global_active_power) as avg_active_power,
                AVG(voltage) as avg_voltage,
                AVG(global_intensity) as avg_intensity,
                AVG(sub_metering_1) as sub_metering_1,
                AVG(sub_metering_2) as sub_metering_2,
                AVG(sub_metering_3) as sub_metering_3
            FROM parquet.`{HDFS_DATA_PATH}`
            WHERE datetime IS NOT NULL
            GROUP BY datetime
            ORDER BY datetime DESC
            LIMIT 100
        """
    
    df = execute_query_python(query_func)
    
    if df.empty:
        return []
    
    # Convertir tipos numéricos
    numeric_cols = ['avg_active_power', 'avg_voltage', 'avg_intensity', 
                    'sub_metering_1', 'sub_metering_2', 'sub_metering_3']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Ordenar ascendente para el gráfico
    df = df.sort_values('datetime')
    df['datetime'] = pd.to_datetime(df['datetime'], errors='coerce').dt.strftime('%Y-%m-%d %H:%M:%S')
    return df.to_dict('records')

def get_hourly_aggregates() -> List[Dict]:
    """Obtiene agregados por hora"""
    def query_func():
        # Leer directamente desde Parquet sin usar tabla Hive
        return f"""
            SELECT 
                HOUR(datetime) as hour,
                AVG(global_active_power) as avg_active_power,
                AVG(voltage) as avg_voltage,
                COUNT(*) as record_count
            FROM parquet.`{HDFS_DATA_PATH}`
            WHERE datetime IS NOT NULL
            GROUP BY HOUR(datetime)
            ORDER BY hour ASC
        """
    
    df = execute_query_python(query_func)
    
    if df.empty:
        return []
    
    # Convertir tipos numéricos
    numeric_cols = ['hour', 'avg_active_power', 'avg_voltage', 'record_count']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    return df.to_dict('records')

