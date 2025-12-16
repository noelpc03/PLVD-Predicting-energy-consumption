# hive_connector.py - Conector para leer datos Parquet desde HDFS usando Spark SQL
import os
import subprocess
import json
import pandas as pd
from typing import Optional, List, Dict
from cache_helper import get_cached, set_cached, cached

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
            '--driver-memory', '512m',  # Mínimo requerido por Spark (471MB)
            '--executor-memory', '512m',
            '--conf', f'spark.hadoop.fs.defaultFS={hdfs_uri}',
            '--conf', f'spark.sql.warehouse.dir={hdfs_uri}/user/hive/warehouse',
            '--conf', 'spark.driver.maxResultSize=128m',  # Reducido tamaño de resultados
            '--conf', 'spark.sql.shuffle.partitions=2',  # Reducir particiones para queries pequeñas
            '--conf', 'spark.default.parallelism=2',  # Reducir paralelismo
            '--conf', 'hive.metastore.uris=thrift://hive-metastore:9083',
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
            # Solo imprimir si es un error real, no warnings
            if 'error' in error_msg.lower() and 'warning' not in error_msg.lower():
                print(f"Error ejecutando Spark SQL: {error_msg[:500]}")
            return pd.DataFrame()
        
        # Parsear JSON output - extraer solo la línea JSON válida
        output_lines = result.stdout.strip().split('\n')
        json_line = None
        
        # Buscar la línea que contiene JSON válido (empieza con [ o { y no contiene logs)
        for line in reversed(output_lines):
            line = line.strip()
            if not line:
                continue
            # Verificar que sea JSON válido (no logs de Spark)
            if (line.startswith('[') or line.startswith('{')) and not line.startswith('[INFO') and not line.startswith('[WARN') and not line.startswith('[ERROR'):
                # Intentar parsear para verificar que sea JSON válido
                try:
                    json.loads(line)
                    json_line = line
                    break
                except json.JSONDecodeError:
                    continue
        
        if not json_line:
            # Si no encontramos JSON, puede ser que el output esté vacío o malformado
            # Intentar buscar en stderr también
            if result.stderr:
                stderr_lines = result.stderr.strip().split('\n')
                for line in reversed(stderr_lines):
                    line = line.strip()
                    if line and (line.startswith('[') or line.startswith('{')):
                        try:
                            json.loads(line)
                            json_line = line
                            break
                        except json.JSONDecodeError:
                            continue
            
            if not json_line:
                return pd.DataFrame()
        
        try:
            data = json.loads(json_line)
            if isinstance(data, dict) and 'error' in data:
                print(f"Error en query: {data['error'][:200]}")
                return pd.DataFrame()
            if isinstance(data, list):
                if len(data) > 0:
                    df = pd.DataFrame(data)
                else:
                    df = pd.DataFrame()
            elif isinstance(data, dict):
                # Si es un solo diccionario, convertir a DataFrame con una fila
                df = pd.DataFrame([data])
            else:
                df = pd.DataFrame()
            return df
        except json.JSONDecodeError as e:
            print(f"Error parseando JSON: {e}")
            print(f"JSON line: {json_line[:200]}")
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

@cached(ttl=30)  # Cachear por 30 segundos (datos recientes)
def get_latest_data(limit: int = 100) -> List[Dict]:
    """Obtiene los últimos N registros"""
    def query_func():
        # Usar tabla Hive registrada (más eficiente que leer directamente Parquet)
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
            FROM {HIVE_TABLE_NAME}
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

@cached(ttl=120)  # Cachear por 2 minutos
def get_statistics() -> Dict:
    """Obtiene estadísticas agregadas"""
    def query_func():
        # Usar tabla Hive registrada
        return f"""
            SELECT 
                COUNT(*) as total_records,
                AVG(global_active_power) as avg_active_power,
                MAX(global_active_power) as max_active_power,
                MIN(global_active_power) as min_active_power,
                AVG(voltage) as avg_voltage,
                AVG(global_intensity) as avg_intensity,
                SUM(sub_metering_1 + sub_metering_2 + sub_metering_3) as total_sub_metering
            FROM {HIVE_TABLE_NAME}
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

@cached(ttl=60)  # Cachear por 1 minuto
def get_time_series_data(hours: int = 24) -> List[Dict]:
    """Obtiene datos de series de tiempo agregados por datetime"""
    def query_func():
        # Usar tabla Hive registrada - optimizado: limitar a 100 registros para mejor performance
        return f"""
            SELECT 
                datetime,
                global_active_power as avg_active_power,
                voltage as avg_voltage,
                global_intensity as avg_intensity,
                sub_metering_1,
                sub_metering_2,
                sub_metering_3
            FROM {HIVE_TABLE_NAME}
            WHERE datetime IS NOT NULL
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

@cached(ttl=300)  # Cachear por 5 minutos (los datos por hora cambian poco)
def get_hourly_aggregates() -> List[Dict]:
    """Obtiene agregados por hora"""
    def query_func():
        # Usar tabla Hive registrada - usar columna hour directamente (ya está particionada)
        return f"""
            SELECT 
                hour,
                AVG(global_active_power) as avg_active_power,
                AVG(voltage) as avg_voltage,
                COUNT(*) as record_count
            FROM {HIVE_TABLE_NAME}
            WHERE datetime IS NOT NULL
            GROUP BY hour
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

