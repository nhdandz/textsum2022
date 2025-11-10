# LUỒNG XỬ LÝ KAFKA - TEXT SUMMARIZATION SYSTEM

## 📊 SƠ ĐỒ LUỒNG HOÀN CHỈNH

```
                    topic_input_ai
                         ↓
              ┌──────────────────────┐
              │   root-kafka         │
              │  (root_kafka.py)     │
              │  Phân loại is_single │
              └──────────┬───────────┘
                         ↓
         ┌───────────────┴────────────────┐
         ↓                                ↓
    single_root                     multi_root
         ↓                                ↓
┌────────────────────┐          ┌────────────────────┐
│   single-kafka     │          │   multi-kafka      │
│  (single_root.py)  │          │  (multi_kafka.py)  │
│  Route thuật toán  │          │  Route thuật toán  │
└────────┬───────────┘          └─────────┬──────────┘
         ↓                                ↓
┌─────────────────────┐         ┌─────────────────────┐
│ Algorithm Topics    │         │ Algorithm Topics    │
│                     │         │                     │
│ • 1_single_lexrank  │         │ • 23_multi_textrank │
│ • 2_single_textrank │         │ • 24_multi_lexrank  │
│ • 3_single_lsa      │         │ • 25_multi_lsa      │
│ • ...               │         │ • ...               │
└─────────┬───────────┘         └─────────┬───────────┘
          ↓                               ↓
┌─────────────────────┐         ┌─────────────────────┐
│ Single Algorithms   │         │ Multi Algorithms    │
│                     │         │                     │
│ • textrank          │         │ • m-textrank        │
│ • lexrank           │         │ • m-lexrank         │
│ • lsa               │         │ • m-lsa             │
└─────────┬───────────┘         └─────────┬───────────┘
          ↓                               ↓
          └───────────────┬───────────────┘
                          ↓
                     result_ai
                          ↓
              ┌──────────────────────┐
              │  result-consumer     │
              │  (test_consum.py)    │
              │  Gửi về Backend API  │
              └──────────────────────┘
                          ↓
                   Backend System
```

## 📝 CHI TIẾT CÁC BƯỚC

### Bước 1: Tiếp nhận và Phân loại
**Service**: `root-kafka`
**File**: `/modules/root_kafka/root_kafka.py`
**Topic Consumer**: `topic_input_ai`
**Topics Producer**: `single_root` hoặc `multi_root`

**Chức năng**:
- Nhận message từ `topic_input_ai`
- Kiểm tra field `is_single` trong message
- Route message:
  - `is_single == True` → gửi vào `single_root`
  - `is_single == False` → gửi vào `multi_root`

---

### Bước 2a: Xử lý Single Document
**Service**: `single-kafka`
**File**: `/modules/single_kafka/single_root.py`
**Topic Consumer**: `single_root`
**Topics Producer**: Dynamic (theo thuật toán)

**Chức năng**:
- Nhận message từ `single_root`
- Trích xuất văn bản từ document (PDF, DOCX, text)
- Phân tích theo topic nếu có keywords
- Gọi API để lấy topic_name từ `id_mapAlgTypeAI`
- Route đến topic thuật toán tương ứng:
  - `id_mapAlgTypeAI=1` → `1_single_lexrank`
  - `id_mapAlgTypeAI=2` → `2_single_textrank`
  - `id_mapAlgTypeAI=3` → `3_single_lsa`

---

### Bước 2b: Xử lý Multi Document
**Service**: `multi-kafka`
**File**: `/modules/root_kafka/multi_kafka.py`
**Topic Consumer**: `multi_root`
**Topics Producer**: Dynamic (theo thuật toán)

**Chức năng**:
- Nhận message từ `multi_root`
- Convert base64 files thành text
- Cluster theo keywords nếu có topic
- Gọi API để lấy topic_name từ `id_mapAlgTypeAI`
- Route đến topic thuật toán tương ứng:
  - `id_mapAlgTypeAI=23` → `23_multi_textrank`
  - `id_mapAlgTypeAI=24` → `24_multi_lexrank`
  - `id_mapAlgTypeAI=25` → `25_multi_lsa`

---

### Bước 3: Xử lý Thuật toán

#### Single Document Algorithms

**TextRank** (service: `textrank`)
- Topic Consumer: `2_single_textrank`
- File: `/modules/Single/TexRank/texrank.py`
- Topic Producer: `result_ai`

**LexRank** (service: `lexrank`)
- Topic Consumer: `1_single_lexrank`
- File: `/modules/Single/TexRank/lexrank.py`
- Topic Producer: `result_ai`

**LSA** (service: `lsa`)
- Topic Consumer: `3_single_lsa`
- File: `/modules/Single/TexRank/lsa.py`
- Topic Producer: `result_ai`

#### Multi Document Algorithms

**Multi TextRank** (service: `m-textrank`)
- Topic Consumer: `23_multi_textrank`
- File: `/modules/Multi/MulTexRank/multi_texrank.py`
- Topic Producer: `result_ai`

**Multi LexRank** (service: `m-lexrank`)
- Topic Consumer: `24_multi_lexrank`
- File: `/modules/Multi/MulTexRank/multi_lexrank.py`
- Topic Producer: `result_ai`

**Multi LSA** (service: `m-lsa`)
- Topic Consumer: `25_multi_lsa`
- File: `/modules/Multi/MulTexRank/multi_lsa.py`
- Topic Producer: `result_ai`

---

### Bước 4: Xử lý Kết quả (MỚI THÊM)
**Service**: `result-consumer`
**File**: `/modules/root_kafka/test_consum.py`
**Topic Consumer**: `result_ai`
**Output**: Backend API

**Chức năng**:
- Nhận kết quả tóm tắt từ topic `result_ai`
- Validate message structure
- Gửi kết quả về Backend API qua HTTP POST
- Log chi tiết quá trình xử lý

**Environment Variables**:
- `KAFKA_BOOTSTRAP_SERVERS`: Kafka server address (default: `kafka:9092`)
- `BACKEND_API_URL`: Backend API endpoint (default: `http://localhost:8000/api/result`)

---

## 🔧 CẤU HÌNH VÀ DEPENDENCIES

### Services trong Docker Compose

| Service | Container | Purpose | Depends On |
|---------|-----------|---------|------------|
| `root-kafka` | root-kafka | Phân loại message | kafka, app-process |
| `single-kafka` | single-kafka | Route single doc | kafka, root-kafka |
| `multi-kafka` | multi-kafka | Route multi doc | kafka, root-kafka |
| `textrank` | textrank | TextRank algorithm | kafka, single-kafka |
| `lexrank` | lexrank | LexRank algorithm | kafka, single-kafka |
| `lsa` | lsa | LSA algorithm | kafka, single-kafka |
| `m-textrank` | m-textrank | Multi TextRank | kafka, multi-kafka |
| `m-lexrank` | m-lexrank | Multi LexRank | kafka, multi-kafka |
| `m-lsa` | m-lsa | Multi LSA | kafka, multi-kafka |
| `result-consumer` | result-consumer | ⭐ Consumer kết quả | kafka |

---

## 📋 KAFKA TOPICS

| Topic | Producer | Consumer | Mô tả |
|-------|----------|----------|-------|
| `topic_input_ai` | External System | root-kafka | Input chính của hệ thống |
| `single_root` | root-kafka | single-kafka | Message văn bản đơn |
| `multi_root` | root-kafka | multi-kafka | Message văn bản đa tài liệu |
| `1_single_lexrank` | single-kafka | lexrank | LexRank single doc |
| `2_single_textrank` | single-kafka | textrank | TextRank single doc |
| `3_single_lsa` | single-kafka | lsa | LSA single doc |
| `23_multi_textrank` | multi-kafka | m-textrank | TextRank multi doc |
| `24_multi_lexrank` | multi-kafka | m-lexrank | LexRank multi doc |
| `25_multi_lsa` | multi-kafka | m-lsa | LSA multi doc |
| `result_ai` | All algorithms | result-consumer | ⭐ Kết quả cuối cùng |

---

## ✅ ĐÃ SỬA

1. ✅ **Hoàn thiện file test_consum.py**
   - Thêm logic xử lý message đầy đủ
   - Thêm logging chi tiết
   - Validate message structure
   - Gửi kết quả về Backend API

2. ✅ **Thêm service result-consumer vào docker-compose.yml**
   - Service mới: `result-consumer`
   - Depends on: `kafka`
   - Command: `python test_consum.py`
   - Environment variables cấu hình

3. ✅ **Kiểm tra luồng hoàn chỉnh**
   - Luồng từ `topic_input_ai` → `result_ai` → Backend đã đầy đủ
   - Tất cả các bước đã được kết nối

---

## 🚀 HƯỚNG DẪN SỬ DỤNG

### 1. Cấu hình Backend API URL

Thêm vào file `.env`:
```bash
BACKEND_API_URL=http://your-backend-api:8000/api/result
```

### 2. Khởi động hệ thống

```bash
docker-compose up -d
```

### 3. Kiểm tra logs

```bash
# Xem log của result-consumer
docker logs -f result-consumer

# Xem log của root-kafka
docker logs -f root-kafka
```

### 4. Test luồng

Gửi message vào `topic_input_ai`:
```bash
python modules/root_kafka/send_data.py
```

### 5. Monitor Kafka topics

Truy cập Kafka UI:
- URL: http://localhost:8080
- Kiểm tra messages trong các topics

---

## 🐛 TROUBLESHOOTING

### Lỗi kết nối Backend
- Kiểm tra `BACKEND_API_URL` trong file `.env`
- Đảm bảo backend service đang chạy
- Kiểm tra network connectivity

### Message không được xử lý
- Kiểm tra logs: `docker logs -f result-consumer`
- Xem Kafka UI để kiểm tra messages trong `result_ai`
- Kiểm tra consumer group status

### Service không start
- Kiểm tra dependencies: `docker-compose ps`
- Kiểm tra Kafka health: `docker logs kafka`
- Restart service: `docker-compose restart result-consumer`

---

## 📊 MONITORING

### Kafka Topics
- Truy cập Kafka UI: http://localhost:8080
- Redpanda Console: http://localhost:8088

### Service Health
```bash
docker-compose ps
docker stats
```

### Consumer Lag
Kiểm tra trong Kafka UI hoặc:
```bash
docker exec -it kafka kafka-consumer-groups --bootstrap-server kafka:9092 --describe --group result_ai_consumer
```
