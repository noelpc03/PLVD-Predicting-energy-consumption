from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, concat_ws, to_timestamp, hour, dayofmonth, month, year,
    dayofweek, when, mean, sum as _sum, stddev, avg
)

# Crear sesión Spark
spark = SparkSession.builder.appName("FeatureEngineering").getOrCreate()

# Leer los datos limpios (ya en formato CSV con punto decimal)
df = (
    spark.read.option("header", True)
        .option("sep", ";")
        .option("inferSchema", True)
        .csv("hdfs:///data/cleaned/")
)

# 1️⃣ Parseo de fecha y hora
df = df.withColumn("datetime", to_timestamp(concat_ws(" ", col("Date"), col("Time")), "dd/MM/yyyy HH:mm:ss"))
df = (
    df.withColumn("year", year("datetime"))
      .withColumn("month", month("datetime"))
      .withColumn("day", dayofmonth("datetime"))
      .withColumn("hour", hour("datetime"))
      .withColumn("weekday", dayofweek("datetime"))
      .withColumn("is_weekend", when(col("weekday").isin(1,7), 1).otherwise(0))
)

# 2️⃣ Features energéticas básicas
df = (
    df.withColumn("Sub_total", col("Sub_metering_1") + col("Sub_metering_2") + col("Sub_metering_3"))
      .withColumn("Power_diff", col("Global_active_power") - col("Global_reactive_power"))
      .withColumn("Power_per_Voltage", col("Global_active_power") / col("Voltage"))
      .withColumn("Reactive_ratio", col("Global_reactive_power") / col("Global_active_power"))
)

# 3️⃣ Agregaciones horarias
agg_hourly = (
    df.groupBy("year", "month", "day", "hour")
      .agg(
          avg("Global_active_power").alias("avg_power_hourly"),
          avg("Voltage").alias("avg_voltage_hourly"),
          avg("Global_intensity").alias("avg_intensity_hourly"),
          _sum("Sub_total").alias("total_sub_hourly")
      )
)

# 4️⃣ Agregaciones diarias
agg_daily = (
    df.groupBy("year", "month", "day")
      .agg(
          avg("Global_active_power").alias("avg_power_daily"),
          stddev("Voltage").alias("voltage_stability_daily"),
          _sum("Sub_total").alias("total_submetering_daily"),
          avg("Global_intensity").alias("avg_intensity_daily")
      )
)

# Guardar resultados
agg_hourly.write.mode("overwrite").parquet("hdfs:///data/features/hourly/")
agg_daily.write.mode("overwrite").parquet("hdfs:///data/features/daily/")

spark.stop()
