#!/usr/bin/env python3
"""
Script para ejecutar queries Spark SQL y retornar resultados en JSON
Se ejecuta dentro del contenedor spark-consumer
"""
import sys
import json
from pyspark.sql import SparkSession

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Query requerida"}))
        sys.exit(1)
    
    query = sys.argv[1]
    
    try:
        # Crear SparkSession con Hive support para usar tablas registradas
        hdfs_uri = sys.argv[2] if len(sys.argv) > 2 else "hdfs://namenode:9000"
        spark = SparkSession.builder \
            .appName("DashboardQuery") \
            .config("spark.sql.warehouse.dir", f"{hdfs_uri}/user/hive/warehouse") \
            .config("spark.hadoop.fs.defaultFS", hdfs_uri) \
            .config("hive.metastore.uris", "thrift://hive-metastore:9083") \
            .enableHiveSupport() \
            .getOrCreate()
        
        # Redirigir logs de Spark a stderr para que no interfieran con stdout
        import logging
        logging.getLogger("py4j").setLevel(logging.ERROR)
        spark.sparkContext.setLogLevel("ERROR")
        
        # Ejecutar query
        df = spark.sql(query)
        
        # Convertir a lista de diccionarios sin pandas
        columns = df.columns
        results = []
        for row in df.collect():
            row_dict = {}
            for i, col in enumerate(columns):
                value = row[i]
                # Convertir tipos que no son JSON serializables
                if hasattr(value, 'isoformat'):  # datetime
                    value = value.isoformat()
                elif value is None:
                    value = None
                elif isinstance(value, (int, float)):
                    # Asegurar que los números sean serializables
                    pass
                row_dict[col] = value
            results.append(row_dict)
        
        spark.stop()
        
        # Imprimir JSON solo al final, después de cerrar Spark
        print(json.dumps(results), file=sys.stdout, flush=True)
        sys.exit(0)
        
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)

if __name__ == "__main__":
    main()

