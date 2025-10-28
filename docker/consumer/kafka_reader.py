from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, TimestampType

# 1️⃣ Crear sesión de Spark con soporte Kafka
spark = SparkSession.builder \
    .appName("KafkaEnergyConsumer") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

# 2️⃣ Leer el stream desde Kafka
df_raw = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", "energy-data") \
    .option("startingOffsets", "latest") \
    .load()

# 3️⃣ Convertir el valor binario en texto
df_parsed = df_raw.selectExpr("CAST(value AS STRING) as message")

# 4️⃣ Definir el esquema del JSON (según tu producer)
schema = StructType([
    StructField("timestamp", StringType()),
    StructField("zone", StringType()),
    StructField("power", DoubleType())
])

# 5️⃣ Parsear el JSON
df_json = df_parsed.select(from_json(col("message"), schema).alias("data")).select("data.*")

# 6️⃣ Mostrar por consola
query = df_json.writeStream \
    .outputMode("append") \
    .format("console") \
    .option("truncate", "false") \
    .start()

query.awaitTermination()
