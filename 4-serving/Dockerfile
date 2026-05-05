# =============================================================================
# TẦNG 4: SERVING LAYER – FastAPI Dockerfile
# Sử dụng Python slim image, không cần Node.js
# =============================================================================
FROM python:3.11-slim

WORKDIR /app

# Cài hệ thống dependencies cần thiết cho httpx, v.v.
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy và cài Python dependencies trước (tận dụng Docker layer cache)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ source code
COPY . .

# Tạo thư mục để mount Spark output volume
RUN mkdir -p /data/spark-output

# Expose port FastAPI
EXPOSE 4000

# Biến môi trường mặc định
ENV PORT=4000
ENV SPARK_OUTPUT_PATH=/data/spark-output
ENV WEBHDFS_URL=http://namenode:9870
ENV CACHE_TTL=30

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
  CMD curl -f http://localhost:4000/api/health || exit 1

# Chạy FastAPI với uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "4000", "--workers", "2"]
