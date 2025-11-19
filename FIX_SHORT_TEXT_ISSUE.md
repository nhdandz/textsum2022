# GIẢI QUYẾT VẤN ĐỀ: VĂN BẢN QUÁ NGẮN SAU KHI LỌC TOPIC

## ❓ VẤN ĐỀ

Bạn nhận được output như sau:

```json
{
  "topic": [{
    "list_doc": [
      "Dự án dược liệu quý: bao gồm: (i). Dự án phát triển vùng trồng dược liệu quý..."
    ],
    "list_doc_id": ["688ec634ccbac25bd52faa0f"],
    "topic_id": 120,
    "algo_id": 24,  // MultiLexRank
    "percent_output": 0.1
  }]
}
```

## 🔍 NGUYÊN NHÂN

### 1. Đây là message TRUNG GIAN, không phải kết quả cuối
- Message này được gửi từ `multi-kafka` → `24_multi_lexrank` (topic Kafka)
- Kết quả cuối cùng sẽ ở topic `result_ai`                                                                                                                                                                                    

### 2. Văn bản sau khi lọc keywords QUÁ NGẮN
- Input gốc: 2 documents
- Sau khi lọc theo keywords: Chỉ còn **1 câu duy nhất**
- Thuật toán không thể tóm tắt văn bản quá ngắn

## 🎯 WORKFLOW ĐẦY ĐỦ

```
┌─────────────────┐
│  Client gửi     │
│  payload với    │
│  keywords       │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────┐
│  multi-kafka                        │
│  ├─ Extract documents               │
│  ├─ Lọc theo keywords:              │
│  │  ["khoa học", "công nghệ"]      │
│  └─ Kết quả: Chỉ còn 1 câu!        │
└────────┬────────────────────────────┘
         │ Gửi message trung gian
         ▼
┌─────────────────────────────────────┐
│  24_multi_lexrank (Kafka topic)     │ ← BẠN ĐANG Ở ĐÂY!
│  Message format:                    │
│  - list_doc: ["văn bản đã lọc"]    │
│  - algo_id: 24                      │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│  m-lexrank container                │
│  ├─ Nhận message                    │
│  ├─ Gọi LexRankSummary()           │
│  ├─ Xử lý tóm tắt                  │
│  └─ Nếu văn bản quá ngắn:          │
│     → Trả về empty hoặc gốc        │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│  result_ai (Kafka topic)            │ ← CẦN XEM Ở ĐÂY!
│  Output format:                     │
│  {                                  │
│    "sumary_id": 306,               │
│    "result": {                      │
│      "topic": [{                    │
│        "text": "Tóm tắt...",      │
│        "topic_id": 120              │
│      }]                             │
│    }                                │
│  }                                  │
└─────────────────────────────────────┘
```

## ✅ GIẢI PHÁP

### Giải pháp 1: Kiểm tra kết quả cuối cùng

```bash
# Chạy script kiểm tra
./check_result_ai.sh 306

# Hoặc thủ công
docker compose exec multi-kafka python3 << 'EOF'
from kafka import KafkaConsumer
import json

consumer = KafkaConsumer(
    'result_ai',
    bootstrap_servers=['kafka-1:9092'],
    auto_offset_reset='earliest',
    value_deserializer=lambda x: json.loads(x.decode('utf-8')),
    consumer_timeout_ms=30000
)

for msg in consumer:
    data = msg.value
    if data.get('sumary_id') == 306:
        print(json.dumps(data, indent=2, ensure_ascii=False))
        break

consumer.close()
EOF
```

### Giải pháp 2: Xem logs thuật toán

```bash
# Xem logs m-lexrank
docker compose logs -f m-lexrank | grep "306"

# Kiểm tra có lỗi không
docker compose logs m-lexrank | grep -i error
```

### Giải pháp 3: Sửa payload để có văn bản dài hơn

**Vấn đề**: Keywords quá strict, lọc quá nhiều

**Giải pháp 3a: Nới lỏng keywords**

```json
{
  "topic": [{
    "keywords": [
      ["dược liệu"],           // ← Chỉ cần 1 keyword thay vì 2
      []
    ],
    "topic_id": 120,
    "id_mapAlgTypeAI": 24
  }]
}
```

**Giải pháp 3b: Thêm nhiều documents hơn**

```json
{
  "original_doc_ids": ["doc1", "doc2", "doc3", "doc4"],  // ← Nhiều hơn
  "documents": [
    { "documents_id": "doc1", ... },
    { "documents_id": "doc2", ... },
    { "documents_id": "doc3", ... },
    { "documents_id": "doc4", ... }
  ]
}
```

**Giải pháp 3c: Tăng page_to để lấy nhiều trang hơn**

```json
{
  "documents": [{
    "documents_id": "doc1",
    "raw_text": "...",
    "file_type": 1,
    "page_from": 0,
    "page_to": 20  // ← Tăng từ 10 lên 20 trang
  }]
}
```

### Giải pháp 4: Test với văn bản đủ dài

```bash
docker compose exec multi-kafka python3 << 'EOF'
from kafka import KafkaProducer
import json, base64

# Văn bản dài hơn, nhiều câu chứa keywords
text = """
Nghiên cứu về khoa học và công nghệ đang phát triển mạnh mẽ.
Các nhà khoa học sử dụng công nghệ AI để phân tích dữ liệu.
Công nghệ blockchain đang được ứng dụng rộng rãi trong khoa học.
Khoa học dữ liệu kết hợp với công nghệ máy học mang lại nhiều đột phá.
Các dự án nghiên cứu khoa học được hỗ trợ bởi công nghệ hiện đại.
Internet vạn vật là một lĩnh vực khoa học và công nghệ đầy tiềm năng.
Nghiên cứu về công nghệ sinh học đang tiến triển trong cộng đồng khoa học.
Công nghệ AI đang thay đổi cách thức nghiên cứu khoa học truyền thống.
"""

encoded = base64.b64encode(text.encode()).decode()

producer = KafkaProducer(
    bootstrap_servers=['kafka-1:9092'],
    value_serializer=lambda x: json.dumps(x).encode('utf-8')
)

payload = {
    "user_id": "test_fix",
    "sumary_id": "test_fix_307",
    "original_doc_ids": ["doc1"],
    "documents": [{
        "documents_id": "doc1",
        "raw_text": encoded,
        "file_type": 0,
        "page_from": 0,
        "page_to": 9999
    }],
    "topic": [{
        "keywords": [["khoa học", "công nghệ"], []],
        "topic_id": 120,
        "id_mapAlgTypeAI": 24
    }],
    "id_mapAlgTypeAI": [],
    "percent_output": 0.1,
    "is_single": False
}

producer.send('topic_input_ai', payload).get(timeout=10)
print(f"✅ Sent! sumary_id: {payload['sumary_id']}")
print("\nKiểm tra kết quả:")
print("  ./check_result_ai.sh test_fix_307")
EOF
```

## 🔧 DEBUG COMMANDS

```bash
# 1. Xem tất cả messages trong result_ai
docker compose exec kafka-1 kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 \
  --topic result_ai \
  --from-beginning \
  --max-messages 10

# 2. Xem logs multi-kafka
docker compose logs -f multi-kafka

# 3. Xem logs m-lexrank
docker compose logs -f m-lexrank

# 4. Kafka UI
# http://localhost:8080
# - Topic: 24_multi_lexrank (message trung gian)
# - Topic: result_ai (kết quả cuối cùng)
```

## 📊 SO SÁNH CÁC STAGE

| Stage | Topic Kafka | Format | Nội dung |
|-------|-------------|--------|----------|
| Input | `topic_input_ai` | Documents gốc | Toàn bộ văn bản chưa lọc |
| Trung gian | `24_multi_lexrank` | list_doc, algo_id | **Văn bản đã lọc theo keywords** ← Bạn thấy cái này |
| Output | `result_ai` | result.topic[].text | **Văn bản tóm tắt cuối cùng** ← Cần xem cái này |

## ❓ FAQ

**Q: Tại sao chỉ có 1 câu sau khi lọc?**
- A: Keywords quá strict. Chỉ có 1 câu trong tất cả documents chứa cả "khoa học" VÀ "công nghệ"

**Q: Làm sao biết văn bản có đủ dài không?**
- A: Xem message trong topic `24_multi_lexrank`. Nếu `list_doc` có nhiều câu (>5 câu) thì OK

**Q: Thuật toán có xử lý văn bản ngắn không?**
- A: Có, nhưng kết quả có thể là:
  - Trả về văn bản gốc (không tóm tắt)
  - Trả về empty string ""
  - Tùy thuộc vào implementation

**Q: Nếu vẫn không có kết quả trong result_ai?**
- A: Kiểm tra:
  1. `docker compose logs m-lexrank | grep error`
  2. `docker compose ps` (container có chạy không?)
  3. Xem Kafka UI: http://localhost:8080

## 🚀 QUICK FIX

**Cách nhanh nhất**: Thay đổi keywords để ít strict hơn

```python
# Thay vì
"keywords": [["khoa học", "công nghệ"], []]  # Phải có CẢ HAI

# Dùng
"keywords": [["khoa học"], []]  # Chỉ cần 1 trong 2
# hoặc
"keywords": [["công nghệ"], []]
```

Sau đó chạy lại test và kiểm tra:

```bash
./check_result_ai.sh <sumary_id>
```

---

**Tóm tắt**: Message bạn thấy là **trung gian**, cần xem kết quả cuối tại topic `result_ai`. Văn bản quá ngắn sau khi lọc, cần nới lỏng keywords hoặc thêm documents.
