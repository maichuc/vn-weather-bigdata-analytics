# =============================================================================
# TẦNG 1: DATA SOURCE LAYER – Dockerfile
# Đóng gói data_generator.py vào container Python nhẹ
# Container này chạy liên tục, sinh weblog và mount volume /data với các service khác
# =============================================================================
FROM python:3.11-slim

# Thiết lập thư mục làm việc trong container
WORKDIR /app

ENV PYTHONUNBUFFERED=1

# Copy toàn bộ source code vào container
COPY . .

# Cài đặt dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Tạo thư mục output cho log files
RUN mkdir -p /data

# Khởi chạy data generator
CMD ["python", "data_generator.py"]
