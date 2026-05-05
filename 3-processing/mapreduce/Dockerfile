# =============================================================================
# TẦNG 3: PROCESSING LAYER – MapReduce Dockerfile
# Sử dụng image Hadoop chính thức, compile và chạy MapReduce job
# =============================================================================
FROM apache/hadoop:3.3.5

USER root

# Sửa lỗi repository của CentOS 7 (đã End-of-Life) và cài đặt công cụ biên dịch Java (javac)
RUN sed -i s/mirror.centos.org/vault.centos.org/g /etc/yum.repos.d/*.repo && \
    sed -i s/^#.*baseurl=http/baseurl=http/g /etc/yum.repos.d/*.repo && \
    sed -i s/^mirrorlist=http/#mirrorlist=http/g /etc/yum.repos.d/*.repo && \
    yum clean all && \
    yum install -y java-1.8.0-openjdk-devel && \
    yum clean all

WORKDIR /app

# Copy source code Java
COPY WeatherAnalyzer.java .

# Script khởi động: compile Java → đóng gói JAR → submit MapReduce job
COPY run_mapreduce.sh .
RUN chmod +x run_mapreduce.sh

CMD ["/app/run_mapreduce.sh"]
