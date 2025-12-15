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

# Configuración de HDFS
# NOTA: Usamos 'hdfs://mycluster' directamente (no 'namenode:9000') porque el cluster
# está configurado con High Availability (HA) en docker-compose.yml
HDFS_USER = os.getenv("HDFS_USER", "amalia")
PROJECT_NAME = os.getenv("PROJECT_NAME", "energy_data")
HIVE_TABLE_NAME = os.getenv("HIVE_TABLE_NAME", "energy_data")

# Path de datos en HDFS usando el nombre del cluster (mycluster) para HA
# Este path es usado por todas las queries SQL para leer datos Parquet
HDFS_DATA_PATH = f"hdfs://mycluster/user/{HDFS_USER}/{PROJECT_NAME}/streaming"

# Path del script spark_query.py dentro del contenedor spark-consumer
# Según docker-compose.yml: volumen ../consumer:/app/consumer, working_dir: /app/consumer
SPARK_QUERY_SCRIPT_PATH = os.getenv("SPARK_QUERY_SCRIPT_PATH", "/app/consumer/spark_query.py")

def _get_spark_query_script_path():
    """
    Obtiene el path correcto del script spark_query.py dentro del contenedor.
    Intenta verificar que el archivo existe, si no, usa paths alternativos.
    
    Returns:
        str: Path del script spark_query.py
    """
    # Paths posibles según la configuración del contenedor
    possible_paths = [
        SPARK_QUERY_SCRIPT_PATH,  # Path absoluto según volumen montado
        "/app/consumer/spark_query.py",  # Path absoluto estándar
        "spark_query.py",  # Path relativo desde working_dir (/app/consumer)
    ]
    
    # Intentar verificar que el archivo existe en el contenedor
    for path in possible_paths:
        try:
            # Verificar si el archivo existe en el contenedor
            check_cmd = ['docker', 'exec', 'spark-consumer', 'test', '-f', path]
            result = subprocess.run(
                check_cmd,
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return path
        except (subprocess.TimeoutExpired, Exception):
            # Si falla la verificación, continuar con el siguiente path
            continue
    
    # Si no se pudo verificar, usar el path por defecto (más probable según docker-compose)
    # El working_dir es /app/consumer, así que el path relativo debería funcionar
    return "spark_query.py"

def execute_spark_sql(query: str) -> pd.DataFrame:
    """Ejecuta una query SQL usando PySpark en el contenedor spark-consumer"""
    try:
        # Obtener el path correcto del script
        script_path = _get_spark_query_script_path()
        
        # Ejecutar script Python usando spark-submit dentro del contenedor de Spark
        hdfs_uri = f"hdfs://mycluster"
        cmd = [
            'docker', 'exec', 'spark-consumer',
            '/opt/spark/bin/spark-submit',
            '--master', 'local[1]',
            '--driver-memory', '512m',  # Reducir memoria del driver
            '--executor-memory', '512m',  # Reducir memoria del executor
            '--conf', f'spark.hadoop.fs.defaultFS={hdfs_uri}',
            '--conf', 'spark.driver.maxResultSize=256m',  # Limitar tamaño de resultados
            script_path,  # Usar el path determinado dinámicamente
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
            # Mensaje de error más informativo
            error_details = (
                f"Error ejecutando Spark SQL:\n"
                f"   Script usado: {script_path}\n"
                f"   Query: {query[:100]}...\n"
                f"   Error: {error_msg[:500]}"
            )
            print(error_details)
            
            # Si el error sugiere que el archivo no existe, proporcionar ayuda adicional
            if "No such file" in error_msg or "cannot find" in error_msg.lower():
                print(
                    f"\n⚠️  El script spark_query.py no se encontró en el path: {script_path}\n"
                    f"   Verifica que:\n"
                    f"   - El volumen está montado correctamente en docker-compose.yml\n"
                    f"   - El archivo consumer/spark_query.py existe en el host\n"
                    f"   - El contenedor spark-consumer está corriendo\n"
                    f"   - El working_dir del contenedor es /app/consumer"
                )
            
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

