# =============================================================================
# TẦNG 3: PROCESSING LAYER – Spark trên YARN – Dockerfile
# Image cần có: Hadoop client (để gọi YARN), Python, PySpark
# =============================================================================
FROM apache/hadoop:3.3.5

USER root

# Sửa lỗi repository CentOS 7 (đã End-of-Life) và cài đặt Python 3, pip
RUN sed -i s/mirror.centos.org/vault.centos.org/g /etc/yum.repos.d/*.repo && \
    sed -i s/^#.*baseurl=http/baseurl=http/g /etc/yum.repos.d/*.repo && \
    sed -i s/^mirrorlist=http/#mirrorlist=http/g /etc/yum.repos.d/*.repo && \
    yum clean all && \
    yum install -y python3 python3-pip python3-devel curl && \
    yum clean all

# Tạo symlink python → python3
RUN ln -sf /usr/bin/python3 /usr/bin/python

# Cài đặt PySpark (phải khớp phiên bản với Hadoop)
COPY requirements.txt /tmp/requirements.txt
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt

WORKDIR /app

# Copy Hadoop config files (YARN client cần core-site.xml và yarn-site.xml)
COPY hadoop-conf/ /etc/hadoop/conf/

# Copy Spark analytics script
COPY spark_analytics.py .

# Script khởi động: chờ YARN sẵn sàng rồi submit job
COPY run_spark_yarn.sh .
RUN chmod +x run_spark_yarn.sh

# Biến môi trường Hadoop/YARN client
ENV HADOOP_CONF_DIR=/etc/hadoop/conf
ENV YARN_CONF_DIR=/etc/hadoop/conf
ENV PYSPARK_PYTHON=python3

CMD ["/app/run_spark_yarn.sh"]
