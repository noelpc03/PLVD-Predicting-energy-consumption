# 01_clean_data.py
from pyspark.sql import SparkSession
from pyspark.sql.functions import to_timestamp, col, trim

spark = SparkSession.builder.appName("clean_energy").getOrCreate()

input_path = "hdfs://namenode:9000/user/amalia/data/dataset.txt"

# Leemos como texto - cada línea contiene un registro; luego parseamos
raw = spark.read.text(input_path)

# Ejemplo: si el txt tiene separador ';' y header en primera línea
# Convertimos a DataFrame con columnas
# Usamos RDD map para parsear rápido y luego toDF (alternativa: read.csv si el archivo es structurado)
header = raw.first()[0]
columns = [c.strip() for c in header.split(";")]

rdd = raw.rdd.zipWithIndex().filter(lambda x: x[1] > 0).map(lambda x: x[0][0].split(";"))
df = rdd.toDF(columns)

# Normalizaciones
df = df.withColumn("DateTime", to_timestamp(col("Date") + " " + col("Time"), "dd/MM/yyyy HH:mm:ss"))
df = df.dropna(subset=["Global_active_power"])
df = df.withColumn("Global_active_power", trim(col("Global_active_power")).cast("double"))

# Filter sanity: valores no negativos y no nulos
df = df.filter(col("Global_active_power") > 0)

# Guardar como Parquet (columnar, óptimo para Spark)
output_path = "hdfs://namenode:9000/user/amalia/data/"
df.write.mode("overwrite").parquet(output_path)

print("Limpieza completada, guardado en:", output_path)
spark.stop()
