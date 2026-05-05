# 📊 Lab 10 – Hệ thống Phân tích Weblogs Thời gian thực mô phỏng

> **Môn học:** Nhập môn Dữ liệu lớn  
> **Đề tài:** Xây dựng Data Pipeline 6 tầng phân tích Weblog theo kiến trúc Big Data  
> **Công nghệ:** Hadoop HDFS · Java MapReduce · **Apache Spark/YARN** · Apache Hive · **FastAPI (Python)** · **Plotly Dash (Python)** · Docker  
> **Ngôn ngữ:** Python (toàn bộ Serving + Visualization) + Java (MapReduce) – **Không dùng JavaScript/TypeScript**

---

## 📋 Mục lục

1. [Tổng quan hệ thống](#1-tổng-quan-hệ-thống)
2. [Kiến trúc 6 tầng](#2-kiến-trúc-6-tầng)
3. [Cấu trúc thư mục](#3-cấu-trúc-thư-mục)
4. [Hướng dẫn cài đặt & chạy](#4-hướng-dẫn-cài-đặt--chạy)
5. [Chi tiết từng tầng](#5-chi-tiết-từng-tầng)
6. [API Endpoints](#6-api-endpoints)
7. [Đánh giá hiệu năng](#7-đánh-giá-hiệu-năng)
8. [Kết luận](#8-kết-luận)

---

## 1. Tổng quan hệ thống

Hệ thống mô phỏng pipeline xử lý **Weblog** theo kiến trúc Big Data end-to-end. **Toàn bộ stack sử dụng Python**, ngoại trừ Java MapReduce và Bash script ingestion.

```
┌─────────────────────────────────────────────────────────────────────┐
│                    DATA PIPELINE – 6 TẦNG                           │
├─────────┬──────────┬──────────┬───────────┬──────────┬─────────────┤
│ LAYER 1 │ LAYER 2  │ LAYER 3  │  LAYER 4  │ LAYER 5  │   LAYER 6   │
│  Data   │Ingestion │ Storage  │Processing │ Serving  │Visualization│
│ Source  │          │  (HDFS)  │(MR+Spark) │(FastAPI) │(Plotly Dash)│
├─────────┼──────────┼──────────┼───────────┼──────────┼─────────────┤
│ Python  │  Bash    │ Hadoop   │MapReduce  │ FastAPI  │ Plotly Dash │
│Generator│ ingest.sh│ NameNode │  + PySpark│ (Python) │  (Python)   │
│         │          │+DataNode │ on YARN   │ Pydantic │  Plotly.py  │
│         │          │+YARN RM  │  + Hive   │          │             │
│         │          │+YARN NM  │           │          │             │
└─────────┴──────────┴──────────┴───────────┴──────────┴─────────────┘
```

### Luồng dữ liệu (Data Flow)

```
data_generator.py (Python)
       │ sinh 2 dòng/giây
       ▼
live_logs.txt (Docker volume)
       │ ingest.sh – batch mỗi 60s
       ▼
HDFS: /user/hadoop/project/input/logs_YYYYMMDD_HHmmss.txt
       │
       ├──── LogAnalyzer.java (MapReduce trên YARN)
       │         └─► HDFS: /output/mapreduce/ (status_code counts)
       │
       └──── spark_analytics.py (PySpark - master=yarn)
                 ├─► HDFS: /output/spark/status_codes/ (CSV)
                 ├─► HDFS: /output/spark/top_urls/ (CSV)
                 └─► Hive: weblog_db.status_codes, weblog_db.top_urls
                                   │
                         FastAPI (Python, port 4000)
                         /api/status-codes
                         /api/top-urls
                         /api/summary
                         /api/docs (Swagger UI tự động)
                                   │
                      Plotly Dash (Python, port 3000)
                      Donut Pie Chart + Horizontal Bar Chart
                      Auto-refresh mỗi 30 giây
```

---

## 2. Kiến trúc 6 tầng

### Tầng 1 – Data Source Layer

| Thành phần | Mô tả |
|-----------|-------|
| `data_generator.py` | Script Python sinh weblog theo định dạng Apache Combined Log Format |
| Tần suất | 2 dòng/giây (~172,800 dòng/ngày) |
| Định dạng | `IP - - [timestamp] "METHOD URL HTTP/1.1" STATUS SIZE "ref" "agent"` |
| Output | `/data/live_logs.txt` (Docker volume) |

### Tầng 2 – Ingestion Layer

| Thành phần | Mô tả |
|-----------|-------|
| `ingest.sh` | Bash script thực hiện Batch Ingestion |
| Chu kỳ | Mỗi 60 giây |
| Pattern | Rolling snapshot – copy log → upload HDFS → truncate |
| Destination | `hdfs://namenode:9000/user/hadoop/project/input/` |

### Tầng 3 – Storage & Processing Layer

| Thành phần | Công nghệ | Mô tả |
|-----------|-----------|-------|
| Storage | Hadoop HDFS 3.3 | Distributed file system, 1 NameNode + 1 DataNode |
| YARN | ResourceManager + NodeManager | Quản lý tài nguyên cluster cho cả MR và Spark |
| Raw Processing | Java MapReduce (trên YARN) | Đếm HTTP Status Code (Mapper → Shuffle → Reducer) |
| Analytics | **PySpark 3.5 (master=yarn)** | Top 10 URLs, phân tích chi tiết, lưu Hive |
| Metadata | Apache Hive 3.1 | SQL interface cho kết quả Spark |

### Tầng 4 – Serving Layer *(Python)*

| Thành phần | Mô tả |
|-----------|-------|
| Framework | **FastAPI** (Python 3.11, async) |
| Endpoints | `GET /api/status-codes`, `/api/top-urls`, `/api/summary`, `/api/health` |
| Docs | Swagger UI tự động: `http://localhost:4000/api/docs` |
| Data source | CSV từ Spark output + WebHDFS fallback + mock data fallback |
| Typing | Pydantic v2 (strict type validation) |
| Cache | In-memory cache, TTL 30 giây |
| Server | Uvicorn ASGI, 2 workers |

### Tầng 5 – Visualization Layer *(Python)*

| Thành phần | Mô tả |
|-----------|-------|
| Framework | **Plotly Dash** (Python) |
| Charts | Plotly – Donut Pie Chart + Horizontal Bar Chart |
| Auto-refresh | `dcc.Interval` – tự gọi API mỗi 30 giây |
| Styling | CSS tùy chỉnh tone nâu/vàng + Dash Bootstrap Components |
| Server | Gunicorn, 2 workers |
| **Không dùng** | JavaScript, TypeScript, Next.js, Recharts, Node.js |

---

## 3. Cấu trúc thư mục

```
bao-cao-cuoi-ki-lab-10/
│
├── 📄 docker-compose.yml             ← Orchestration toàn bộ hệ thống
├── 📄 README.md                      ← Báo cáo này
│
├── 📁 1-data-source/                 ← TẦNG 1: Data Source (Python)
│   ├── data_generator.py
│   ├── requirements.txt
│   └── Dockerfile
│
├── 📁 2-ingestion/                   ← TẦNG 2: Ingestion
│   └── ingest.sh
│
├── 📁 3-processing/                  ← TẦNG 3: Processing
│   ├── mapreduce/
│   │   ├── LogAnalyzer.java          ← MapReduce: đếm Status Code (trên YARN)
│   │   ├── run_mapreduce.sh
│   │   └── Dockerfile
│   └── spark/
│       ├── spark_analytics.py        ← PySpark: --master yarn
│       ├── run_spark_yarn.sh         ← Submit job lên YARN
│       ├── requirements.txt
│       ├── hadoop-conf/
│       │   ├── core-site.xml         ← HDFS config cho Spark client
│       │   └── yarn-site.xml         ← YARN config cho Spark client
│       └── Dockerfile
│
├── 📁 4-serving/                     ← TẦNG 4: Serving API (FastAPI Python)
│   ├── main.py                       ← FastAPI app + endpoints
│   ├── models/
│   │   └── schemas.py                ← Pydantic models (strict typing)
│   ├── services/
│   │   └── hdfs_reader.py            ← Đọc CSV từ HDFS/local
│   ├── requirements.txt
│   └── Dockerfile
│
└── 📁 5-visualization/               ← TẦNG 5: Dashboard (Plotly Dash Python)
    ├── app.py                        ← Dash app entry point
    ├── layouts/
    │   └── main_layout.py            ← Toàn bộ UI layout
    ├── components/
    │   ├── status_chart.py           ← Donut Pie Chart (Plotly)
    │   └── topurl_chart.py           ← Horizontal Bar Chart (Plotly)
    ├── assets/
    │   └── custom.css                ← CSS tone nâu/vàng
    ├── requirements.txt
    └── Dockerfile
```

---

## 4. Hướng dẫn cài đặt & chạy

### Yêu cầu hệ thống

| Yêu cầu | Tối thiểu | Khuyến nghị |
|---------|-----------|-------------|
| RAM | 8 GB | 16 GB |
| CPU | 4 cores | 8 cores |
| Disk | 20 GB | 50 GB |
| Docker | 24.0+ | Latest |
| Docker Compose | 2.20+ | Latest |

### Bước 1: Clone và chuẩn bị

```bash
git clone <repository-url>
cd bao-cao-cuoi-ki-lab-10
docker --version && docker compose version
```

### Bước 2: Build và chạy toàn bộ hệ thống

```bash
# Build tất cả images và khởi động (lần đầu mất ~5-10 phút)
docker-compose up --build -d

# Theo dõi logs toàn bộ hệ thống
docker-compose logs -f

# Theo dõi log của service cụ thể
docker-compose logs -f data-generator
docker-compose logs -f spark-analytics   # PySpark YARN job
docker-compose logs -f fastapi
```

### Bước 3: Kiểm tra trạng thái

```bash
# Xem trạng thái tất cả containers
docker-compose ps

# Kiểm tra HDFS có data chưa
docker exec lab10-namenode hdfs dfs -ls /user/hadoop/project/input/

# Kiểm tra kết quả MapReduce
docker exec lab10-namenode hdfs dfs -cat /user/hadoop/project/output/mapreduce/part-r-*

# Kiểm tra kết quả Spark/YARN trên Hive
docker exec lab10-hive-metastore hive -e "SELECT * FROM weblog_db.top_urls LIMIT 10;"

# Kiểm tra FastAPI
curl http://localhost:4000/api/health
curl http://localhost:4000/api/status-codes | python -m json.tool
curl http://localhost:4000/api/top-urls | python -m json.tool
```

### Bước 4: Truy cập các giao diện

| Service | URL | Mô tả |
|---------|-----|-------|
| **Dashboard** | http://localhost:3000 | Plotly Dash Dashboard (**giao diện chính**) |
| **FastAPI Docs** | http://localhost:4000/api/docs | Swagger UI tự động |
| **FastAPI ReDoc** | http://localhost:4000/api/redoc | ReDoc alternative |
| **HDFS Web UI** | http://localhost:9870 | Hadoop NameNode Web UI |
| **YARN Resource Manager** | http://localhost:8088 | YARN cluster monitoring (jobs, containers) |
| **YARN NodeManager** | http://localhost:8042 | NodeManager Web UI |

### Bước 5: Chạy lại các job xử lý

```bash
# Chạy lại MapReduce job thủ công
docker restart lab10-mapreduce

# Chạy lại Spark/YARN Analytics thủ công
docker restart lab10-spark-analytics

# Dừng toàn bộ hệ thống
docker-compose down

# Dừng và xóa volumes (reset data)
docker-compose down -v
```

### Troubleshooting

```bash
# Kiểm tra YARN cluster thông qua REST API
curl http://localhost:8088/ws/v1/cluster/info

# Xem các YARN applications đang chạy
curl http://localhost:8088/ws/v1/cluster/apps

# Nếu Spark YARN bị lỗi: kiểm tra logs
docker logs lab10-spark-analytics --tail 200

# Vào shell container để debug
docker exec -it lab10-namenode bash
docker exec -it lab10-fastapi bash
docker exec -it lab10-plotly-dashboard bash

# Chạy Spark YARN job thủ công từ trong container
docker exec -it lab10-spark-analytics bash
# Trong container:
# spark-submit --master yarn --deploy-mode client /app/spark_analytics.py
```

---

## 5. Chi tiết từng tầng

### Tầng 3 – PySpark trên YARN

```python
# Kết nối YARN thay vì Standalone
spark = (
    SparkSession.builder
    .appName("WebLog Analytics - Lab 10 (YARN)")
    .master("yarn")                        # ← YARN ResourceManager
    .config("spark.submit.deployMode", "client")
    .config("spark.executor.memory", "1g")
    .config("spark.executor.instances", "2")  # 2 executors trên YARN
    .config("spark.yarn.queue", "default")
    .enableHiveSupport()
    .getOrCreate()
)
```

**Ưu điểm YARN so với Standalone:**
- Tận dụng chung ResourceManager với MapReduce
- Quản lý tài nguyên tập trung, tránh over-provisioning
- Hỗ trợ Queue (fair scheduling giữa các job)
- Dynamic allocation (tự động tăng/giảm executor)

### Tầng 4 – FastAPI (Python)

```python
# main.py – FastAPI app
@app.get("/api/status-codes", response_model=ApiResponse[list[StatusCodeRecord]])
async def get_status_codes() -> ApiResponse[list[StatusCodeRecord]]:
    data = hdfs_service.get_status_codes()
    return ApiResponse(success=True, data=data, count=len(data), ...)

# models/schemas.py – Pydantic v2 strict typing
class StatusCodeRecord(BaseModel):
    model_config = ConfigDict(frozen=True)
    status_code: int = Field(..., ge=100, le=599)
    count: int = Field(..., ge=0)
    percentage: float = Field(..., ge=0.0, le=100.0)
    description: str
```

### Tầng 5 – Plotly Dash (Python)

```python
# app.py – Dash callback
@callback(
    Output("status-code-graph", "figure"),
    Output("top-urls-graph", "figure"),
    Output("metric-total-requests", "children"),
    Input("interval-refresh", "n_intervals"),  # Auto-refresh mỗi 30s
)
def update_all_charts(n_intervals):
    response = requests.get(f"{API_BASE_URL}/api/summary")
    data = response.json()["data"]
    return (
        create_status_code_figure(data["status_codes"]),
        create_top_urls_figure(data["top_urls"]),
        format_number(data["total_requests"]),
    )
```

---

## 6. API Endpoints

### `GET /api/health`

```json
{
  "status": "ok",
  "timestamp": "2024-05-05T16:30:00.000000Z",
  "data_source": "/data/spark-output",
  "records": { "status_codes": 8, "top_urls": 10 }
}
```

### `GET /api/status-codes`

```json
{
  "success": true,
  "data": [
    { "status_code": 200, "count": 15420, "percentage": 70.0, "description": "OK" },
    { "status_code": 404, "count": 2200, "percentage": 10.0, "description": "Not Found" }
  ],
  "count": 8,
  "timestamp": "2024-05-05T16:30:00.000000Z",
  "message": "Đã tìm thấy 8 loại HTTP Status Code trong weblog."
}
```

### `GET /api/top-urls`

```json
{
  "success": true,
  "data": [
    { "url": "/home", "request_count": 4520, "avg_response_size": 12500, "unique_visitors": 1230 }
  ],
  "count": 10,
  "timestamp": "2024-05-05T16:30:00.000000Z",
  "message": "Top 10 URL được truy cập nhiều nhất theo phân tích Spark/YARN."
}
```

**Swagger UI tự động:** http://localhost:4000/api/docs

---

## 7. Đánh giá hiệu năng

> **Hướng dẫn:** Điền kết quả sau khi chạy thực nghiệm trên Cloud

### 7.1 Thông số môi trường thực nghiệm

| Thông số | Giá trị |
|---------|---------|
| Nền tảng Cloud | _(AWS EMR / Google Dataproc)_ |
| Số node YARN | _(1 ResourceManager + N NodeManager)_ |
| Instance type | _(ví dụ: m5.xlarge – 4 vCPU, 16 GB RAM)_ |
| Phiên bản Hadoop | 3.3.5 |
| Phiên bản Spark | 3.5.0 |

### 7.2 Kết quả MapReduce (trên YARN)

| Metric | Giá trị |
|--------|---------|
| Kích thước dữ liệu | ___ MB / ___ GB |
| Số dòng log | ___ |
| Số Mapper | ___ |
| Số Reducer | 2 |
| Thời gian tổng | ___ giây |
| Thời gian Map phase | ___ giây |
| Thời gian Reduce phase | ___ giây |

### 7.3 Kết quả PySpark (trên YARN)

| Metric | Giá trị |
|--------|---------|
| Kích thước dữ liệu | ___ MB / ___ GB |
| Số YARN Container | ___ |
| Số Spark partitions | ___ |
| Thời gian SparkSession init | ___ giây |
| Thời gian đọc HDFS | ___ giây |
| Thời gian tính Top URLs | ___ giây |
| Thời gian ghi Hive | ___ giây |
| Tổng thời gian job | ___ giây |

### 7.4 So sánh MapReduce vs PySpark (YARN)

| Tiêu chí | MapReduce (YARN) | PySpark (YARN) |
|---------|------------------|----------------|
| Thời gian 1 GB | ___ giây | ___ giây |
| Thời gian 10 GB | ___ giây | ___ giây |
| Ngôn ngữ | Java | Python |
| Quản lý tài nguyên | YARN | YARN |
| Độ phức tạp | Cao | Thấp |
| In-memory caching | Không | Có |

### 7.5 Hiệu năng FastAPI

| Endpoint | Latency P50 | Latency P95 |
|---------|------------|------------|
| `GET /api/health` | ___ ms | ___ ms |
| `GET /api/status-codes` | ___ ms | ___ ms |
| `GET /api/top-urls` | ___ ms | ___ ms |
| `GET /api/summary` | ___ ms | ___ ms |

---

## 8. Kết luận

### Những gì đã đạt được

1. ✅ **Python-only stack** – Serving và Visualization hoàn toàn bằng Python
2. ✅ **Spark trên YARN** – tận dụng chung cluster với MapReduce
3. ✅ **FastAPI** thay NestJS – type-safe với Pydantic, Swagger UI tự động
4. ✅ **Plotly Dash** thay Next.js – biểu đồ tương tác, không cần JavaScript
5. ✅ **Containerization hoàn toàn** – `docker-compose up --build -d` là đủ
6. ✅ **Fault tolerant** – mock data fallback, health checks, restart policies

### Bài học rút ra

- **YARN** cho phép MapReduce và Spark chia sẻ tài nguyên cluster hiệu quả
- **FastAPI** nhanh hơn Flask, type-safe, có Swagger UI tự sinh
- **Plotly Dash** = Python-native dashboard, không cần frontend developer
- **Pydantic v2** đảm bảo data validation chặt chẽ ở Serving Layer

---

## 📎 Tài liệu tham khảo

- [Apache Hadoop YARN](https://hadoop.apache.org/docs/r3.3.5/hadoop-yarn/hadoop-yarn-site/)
- [Apache Spark on YARN](https://spark.apache.org/docs/3.5.0/running-on-yarn.html)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Plotly Dash Documentation](https://dash.plotly.com/)
- [Pydantic v2 Documentation](https://docs.pydantic.dev/latest/)
- [Docker Compose Reference](https://docs.docker.com/compose/)

---

*Lab 10 – Nhập môn Dữ liệu lớn | Python · Hadoop · Spark/YARN · Hive · FastAPI · Plotly Dash · Docker*
