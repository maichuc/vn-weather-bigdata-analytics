#!/bin/bash
# =============================================================================
# Script: run_mapreduce.sh
# Mục đích: Biên dịch và thực thi WeatherAnalyzer MapReduce job trên YARN.
# =============================================================================

INPUT_PATH="/user/hadoop/project/input"
OUTPUT_PATH="/user/hadoop/project/output/mapreduce"
HADOOP_CLASSPATH=$(hadoop classpath)

echo "[MapReduce] Đang dọn dẹp thư mục output cũ trên HDFS..."
hdfs dfs -rm -r -f $OUTPUT_PATH

echo "[MapReduce] Đang biên dịch WeatherAnalyzer.java..."
javac -classpath $HADOOP_CLASSPATH WeatherAnalyzer.java
jar cf weather.jar WeatherAnalyzer*.class

echo "[MapReduce] Bắt đầu thực thi MapReduce Job trên YARN..."
start_time=$(date +%s)

hadoop jar weather.jar WeatherAnalyzer $INPUT_PATH $OUTPUT_PATH

end_time=$(date +%s)
duration=$((end_time - start_time))

echo "[MapReduce] Hoàn thành. Thời gian thực thi: $duration giây."

# Ghi kết quả thời gian vào volume chung để FastAPI đọc
mkdir -p /data/spark-output
echo $duration > /data/spark-output/mr_time.txt

echo "[MapReduce] Kết quả Benchmark đã được ghi vào mr_time.txt"
