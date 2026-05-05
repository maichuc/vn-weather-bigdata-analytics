# =============================================================================
# TẦNG 5: VISUALIZATION LAYER – Plotly Dash Dockerfile
# Python-only, không cần Node.js
# =============================================================================
FROM python:3.11-slim

WORKDIR /app

# Cài hệ thống dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Cài Python dependencies (tận dụng Docker layer cache)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ source code Dash app
COPY . .

# Biến môi trường
ENV FASTAPI_URL=http://fastapi:4000
ENV PORT=3000

EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
  CMD curl -f http://localhost:3000/ || exit 1

# Production: dùng gunicorn với 2 worker
CMD ["gunicorn", "app:server", "--bind", "0.0.0.0:3000", "--workers", "2", "--timeout", "60"]
