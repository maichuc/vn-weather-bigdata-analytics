#!/bin/bash
# =============================================================================
# Script submit PySpark job lên YARN ResourceManager
# Chờ YARN sẵn sàng trước khi submit để tránh lỗi connection refused
# =============================================================================

set -euo pipefail

echo "[Spark/YARN] Waiting for YARN ResourceManager..."

# Chờ YARN ResourceManager (port 8088) phản hồi
MAX_WAIT=120
WAITED=0
until curl -sf "http://resourcemanager:8088/ws/v1/cluster/info" > /dev/null 2>&1; do
    if [ $WAITED -ge $MAX_WAIT ]; then
        echo "[Spark/YARN] YARN failed to start after ${MAX_WAIT}s. Exiting."
        exit 1
    fi
    echo "[Spark/YARN] Waiting for YARN... (${WAITED}s/${MAX_WAIT}s)"
    sleep 10
    WAITED=$((WAITED + 10))
done

echo "[Spark/YARN] YARN is ready! Waiting for data in HDFS..."
sleep 15

echo "[Spark/YARN] Submitting PySpark job to YARN..."

# spark-submit với --master yarn
spark-submit \
    --master yarn \
    --deploy-mode client \
    --name "Weather-Analytics-Lab10" \
    --conf spark.executor.memory=1g \
    --conf spark.executor.cores=1 \
    --conf spark.executor.instances=2 \
    --conf spark.driver.memory=512m \
    --conf spark.yarn.queue=default \
    --conf spark.sql.shuffle.partitions=4 \
    --conf hive.metastore.uris=thrift://hive-metastore:9083 \
    /app/spark_analytics.py

echo "[Spark/YARN] Job completed!"

# SYNC KẾT QUẢ TỪ HDFS VỀ LOCAL VOLUME ĐỂ FASTAPI ĐỌC
echo "[Spark/YARN] Syncing results from HDFS to local volume..."
mkdir -p /data/spark-output/details
hadoop fs -get -f /user/hadoop/project/output/spark/details/*.csv /data/spark-output/details/

echo "[Spark/YARN] Done. Results are ready for Serving Layer."
