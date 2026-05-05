#!/bin/bash
# =============================================================================
# TẦNG 2: INGESTION LAYER
# File: ingest.sh
# Mục đích: Tự động đẩy file log từ local storage lên HDFS theo chu kỳ (Batch Ingestion).
#           Đây là bước kết nối giữa Data Source Layer và Storage Layer.
# Chu kỳ: Mỗi 60 giây đọc logs mới và upload lên HDFS
# =============================================================================

set -euo pipefail

# -----------------------------------------------------------------------
# Cấu hình đường dẫn
# -----------------------------------------------------------------------
# Đường dẫn file log local (được mount từ data-source container)
LOCAL_LOG_FILE="/data/weather_data.json"

# Thư mục HDFS đích – nơi Spark và MapReduce sẽ đọc dữ liệu
HDFS_INPUT_DIR="/user/hadoop/project/input"

# Thư mục tạm để lưu snapshot của log trước khi upload
TMP_DIR="/tmp/weblog_ingestion"

# Số giây giữa mỗi lần batch ingestion
BATCH_INTERVAL=60

# Địa chỉ HDFS NameNode
HDFS_NAMENODE="hdfs://namenode:9000"

# -----------------------------------------------------------------------
# Hàm tiện ích
# -----------------------------------------------------------------------
log_info() {
    echo "[INGESTION $(date '+%Y-%m-%d %H:%M:%S')] INFO: $1"
}

log_error() {
    echo "[INGESTION $(date '+%Y-%m-%d %H:%M:%S')] ERROR: $1" >&2
}

# Kiểm tra HDFS có sẵn sàng chưa (chờ NameNode khởi động)
wait_for_hdfs() {
    log_info "Đang chờ HDFS NameNode sẵn sàng..."
    local max_attempts=30
    local attempt=0

    while [ $attempt -lt $max_attempts ]; do
        if hdfs dfs -ls / > /dev/null 2>&1; then
            log_info "HDFS đã sẵn sàng!"
            return 0
        fi
        attempt=$((attempt + 1))
        log_info "Lần thử $attempt/$max_attempts – HDFS chưa sẵn sàng, thử lại sau 10 giây..."
        sleep 10
    done

    log_error "HDFS không khởi động được sau $max_attempts lần thử. Thoát."
    exit 1
}

# Tạo thư mục HDFS nếu chưa tồn tại
init_hdfs_dirs() {
    log_info "Khởi tạo cấu trúc thư mục HDFS..."
    hdfs dfs -mkdir -p "${HDFS_INPUT_DIR}"
    hdfs dfs -mkdir -p "/user/hadoop/project/output/mapreduce"
    hdfs dfs -mkdir -p "/user/hadoop/project/output/spark"
    log_info "Đã tạo cấu trúc thư mục HDFS: ${HDFS_INPUT_DIR}"
}

# Đẩy logs lên HDFS – đây là hành động Batch Ingestion chính
ingest_logs() {
    # Đặt tên file theo timestamp để không bị ghi đè – tạo thành công partition theo thời gian
    local timestamp
    timestamp=$(date '+%Y%m%d_%H%M%S')
    local snapshot_file="${TMP_DIR}/weather_${timestamp}.txt"

    # Kiểm tra file log nguồn tồn tại
    if [ ! -f "${LOCAL_LOG_FILE}" ]; then
        log_info "File log chưa tồn tại: ${LOCAL_LOG_FILE}. Chờ data generator..."
        return 0
    fi

    # Lấy số dòng hiện tại của file log
    local line_count
    line_count=$(wc -l < "${LOCAL_LOG_FILE}" 2>/dev/null || echo "0")

    if [ "$line_count" -eq 0 ]; then
        log_info "File log trống. Bỏ qua lần ingestion này."
        return 0
    fi

    log_info "Đang tạo snapshot: ${line_count} dòng log → ${snapshot_file}"

    # Tạo snapshot bất biến (immutable) của log hiện tại
    # Dùng cp thay vì move để data_generator vẫn tiếp tục ghi
    cp "${LOCAL_LOG_FILE}" "${snapshot_file}"

    # Truncate file gốc sau khi snapshot (rolling log pattern)
    > "${LOCAL_LOG_FILE}"

    # Upload snapshot lên HDFS (Batch Ingestion)
    log_info "Đang upload lên HDFS: ${HDFS_INPUT_DIR}/weather_${timestamp}.txt"
    if hdfs dfs -put "${snapshot_file}" "${HDFS_INPUT_DIR}/weather_${timestamp}.txt"; then
        log_info "✓ Upload thành công: ${line_count} dòng log → HDFS"
        # Xóa file tạm sau khi upload thành công
        rm -f "${snapshot_file}"
    else
        log_error "Upload thất bại. Giữ lại file tạm: ${snapshot_file}"
    fi
}

# -----------------------------------------------------------------------
# Hàm chính
# -----------------------------------------------------------------------
main() {
    log_info "=== INGESTION SERVICE KHỞI ĐỘNG ==="
    log_info "Source: ${LOCAL_LOG_FILE}"
    log_info "Destination: ${HDFS_NAMENODE}${HDFS_INPUT_DIR}"
    log_info "Batch interval: ${BATCH_INTERVAL} giây"

    # Tạo thư mục tạm
    mkdir -p "${TMP_DIR}"

    # Chờ HDFS sẵn sàng
    wait_for_hdfs

    # Khởi tạo thư mục HDFS
    init_hdfs_dirs

    log_info "Bắt đầu vòng lặp Batch Ingestion..."

    # Vòng lặp ingestion chạy vô hạn
    while true; do
        log_info "--- Bắt đầu batch ingestion ---"
        ingest_logs
        log_info "--- Hoàn thành. Ngủ ${BATCH_INTERVAL} giây ---"
        sleep "${BATCH_INTERVAL}"
    done
}

# Chạy hàm main
main "$@"
