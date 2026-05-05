#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
TẦNG 3: PROCESSING LAYER – Spark Weather Analytics (Support Rain)
File: spark/spark_analytics.py
=============================================================================
"""

import os
import sys
import time
from pyspark.sql import SparkSession, Window
from pyspark.sql.functions import col, from_json, current_timestamp, rank, avg, max, min, desc
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, IntegerType

# Cấu hình đường dẫn HDFS
HDFS_INPUT = "hdfs://namenode:9000/user/hadoop/project/input/"
HDFS_OUTPUT_BASE = "hdfs://namenode:9000/user/hadoop/project/output/spark"

# Schema cho dữ liệu JSON từ API
weather_schema = StructType([
    StructField("province", StringType(), True),
    StructField("temp", DoubleType(), True),
    StructField("humidity", IntegerType(), True),
    StructField("pressure", IntegerType(), True),
    StructField("description", StringType(), True),
    StructField("wind_speed", DoubleType(), True),
    StructField("rain_1h", DoubleType(), True),
    StructField("lat", DoubleType(), True),
    StructField("lon", DoubleType(), True),
    StructField("timestamp", StringType(), True)
])

def main():
    start_time = time.time()
    
    # Khởi tạo Spark Session
    spark = SparkSession.builder \
        .appName("WeatherAnalytics") \
        .config("spark.sql.warehouse.dir", "hdfs://namenode:9000/user/hive/warehouse") \
        .enableHiveSupport() \
        .getOrCreate()

    print(f"[Spark/YARN] Reading data from HDFS: {HDFS_INPUT}")
    
    # Đọc dữ liệu JSON
    raw_df = spark.read.text(HDFS_INPUT)
    
    # Parse JSON
    parsed_df = raw_df.select(from_json(col("value"), weather_schema).alias("data")).select("data.*")
    
    # Lấy bản ghi mới nhất cho mỗi tỉnh thành (Deduplication)
    window_spec = Window.partitionBy("province").orderBy(desc("timestamp"))
    latest_df = parsed_df.withColumn("rank", rank().over(window_spec)) \
        .filter(col("rank") == 1) \
        .drop("rank")

    # Tính toán thống kê tổng quan
    summary_df = latest_df.select(
        avg("temp").alias("avg_temp"),
        max("temp").alias("max_temp_val"),
        min("temp").alias("min_temp_val"),
        max("rain_1h").alias("max_rain_val")
    )
    
    # Lưu kết quả chi tiết xuống HDFS (CSV để Serving layer đọc nhanh)
    details_path = f"{HDFS_OUTPUT_BASE}/details"
    latest_df.coalesce(1).write.mode("overwrite").option("header", "true").csv(details_path)
    print(f"[Spark/YARN] Result saved to {details_path}")

    # Ghi vào Hive Table (Nếu cần)
    spark.sql("CREATE DATABASE IF NOT EXISTS weather_db")
    latest_df.write.mode("overwrite").saveAsTable("weather_db.weather_details")

    duration = int(time.time() - start_time)
    print(f"[Spark/YARN] Completed. Duration: {duration} seconds.")
    
    # Ghi thời gian xử lý ra file local (thông qua volume mount)
    with open("/data/spark-output/spark_time.txt", "w") as f:
        f.write(str(duration))

    spark.stop()

if __name__ == "__main__":
    main()
