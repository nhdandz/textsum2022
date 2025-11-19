# HƯỚNG DẪN TEST THUẬT TOÁN MULTI VỚI TOPIC

## 📊 Phân tích Payload của bạn

```json
{
  "topic": [{
    "keywords": [["khoa học", "công nghệ"], []],
    "topic_id": 120,
    "id_mapAlgTypeAI": 17  // HiMap algorithm
  }],
  "percent_output": 0.1,
  "is_single": false  // Multi-document
}
```

**id_mapAlgTypeAI: 17** → **HiMap (Abstractive, Long Document)**

---

## 🎯 CÁCH TEST NHANH

### Bước 1: Vào container có kafka-python

```bash
docker compose exec multi-kafka bash
```

### Bước 2: Tạo file test

```bash
cat > /tmp/test_multi_topic.py << 'ENDOFFILE'
#!/usr/bin/env python3
from kafka import KafkaProducer
import json
import base64

# Sample text về khoa học công nghệ
text1 = """
Trí tuệ nhân tạo đang cách mạng hóa lĩnh vực khoa học và công nghệ.
Machine learning là công nghệ tiên tiến nhất hiện nay.
Các nhà khoa học đang phát triển thuật toán mới.
Công nghệ blockchain đang được nghiên cứu rộng rãi.
"""

text2 = """
Nghiên cứu về khoa học dữ liệu đang phát triển với công nghệ mới.
Quantum computing là công nghệ đột phá trong khoa học.
Trí tuệ nhân tạo giúp tự động hóa nghiên cứu khoa học.
"""

# Encode base64
doc1 = base64.b64encode(text1.encode('utf-8')).decode('utf-8')
doc2 = base64.b64encode(text2.encode('utf-8')).decode('utf-8')

payload = {
    "user_id": "test_user_123",
    "sumary_id": "test_topic_120",
    "original_doc_ids": ["doc1", "doc2"],
    "documents": [
        {
            "documents_id": "doc1",
            "raw_text": doc1,
            "file_type": 0,
            "page_from": 0,
            "page_to": 9999
        },
        {
            "documents_id": "doc2",
            "raw_text": doc2,
            "file_type": 0,
            "page_from": 0,
            "page_to": 9999
        }
    ],
    "topic": [{
        "keywords": [["khoa học", "công nghệ"], []],
        "topic_id": 120,
        "id_mapAlgTypeAI": 23  # MultiTexRank (có sẵn)
    }],
    "id_mapAlgTypeAI": [],
    "percent_output": 0.1,
    "is_single": False
}

# Gửi đến Kafka
producer = KafkaProducer(
    bootstrap_servers=['kafka-1:9092'],
    max_request_size=100000000,
    value_serializer=lambda x: json.dumps(x).encode('utf-8')
)

print("Gửi message...")
future = producer.send('topic_input_ai', payload)
result = future.get(timeout=10)

print(f"✅ Đã gửi thành công!")
print(f"   Summary ID: {payload['sumary_id']}")
print(f"   Topic ID: {payload['topic'][0]['topic_id']}")
print(f"   Algorithm: {payload['topic'][0]['id_mapAlgTypeAI']}")
print(f"   Offset: {result.offset}")

producer.close()
ENDOFFILE
```

### Bước 3: Chạy test

```bash
python3 /tmp/test_multi_topic.py
```

### Bước 4: Xem logs xử lý

```bash
# Terminal 1: Xem logs multi-kafka
docker compose logs -f multi-kafka

# Terminal 2: Xem logs thuật toán
docker compose logs -f m-textrank m-lexrank m-lsa

# Terminal 3: Kiểm tra Kafka UI
# Mở browser: http://localhost:8080
```

---

## 🔍 KIỂM TRA KẾT QUẢ

### Cách 1: Xem Kafka UI
1. Mở http://localhost:8080
2. Vào topic `output_topic`
3. Tìm message với `sumary_id: "test_topic_120"`

### Cách 2: Đọc từ consumer

```bash
docker compose exec multi-kafka python3 << 'EOF'
from kafka import KafkaConsumer
import json

consumer = KafkaConsumer(
    'output_topic',
    bootstrap_servers=['kafka-1:9092'],
    auto_offset_reset='earliest',
    value_deserializer=lambda x: json.loads(x.decode('utf-8')),
    consumer_timeout_ms=10000
)

print("Đang tìm kết quả...")
for msg in consumer:
    data = msg.value
    if data.get('sumary_id') == 'test_topic_120':
        print("\n✅ TÌM THẤY KẾT QUẢ!")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        break
else:
    print("❌ Chưa tìm thấy kết quả. Có thể đang xử lý...")

consumer.close()
EOF
```

---

## 📝 TEST CÁC THUẬT TOÁN KHÁC

Thay đổi `id_mapAlgTypeAI` trong payload:

```python
"id_mapAlgTypeAI": 23  # MultiTexRank (extractive)
"id_mapAlgTypeAI": 24  # MultiLexRank (extractive)
"id_mapAlgTypeAI": 25  # MultiLSA (extractive)
"id_mapAlgTypeAI": 17  # HiMap (nếu có container)
```

---

## ❓ TROUBLESHOOTING

### Lỗi: Không nhận được kết quả

**Kiểm tra:**
```bash
# 1. Services có chạy không?
docker compose ps

# 2. Xem logs có lỗi không?
docker compose logs multi-kafka | grep -i error
docker compose logs m-textrank | grep -i error

# 3. Kiểm tra Kafka có message không?
docker compose exec kafka-1 kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 \
  --topic topic_input_ai \
  --from-beginning \
  --max-messages 1
```

### Lỗi: Module not found

```bash
# Vào container và cài đặt
docker compose exec multi-kafka bash
pip3 install kafka-python
```

### Văn bản quá ngắn sau khi lọc topic

**Giải pháp**: Thêm nhiều văn bản hơn chứa keywords "khoa học" và "công nghệ"

---

## 🎨 CUSTOM TEST

### Test với keywords khác

```python
"topic": [{
    "keywords": [
        ["AI", "machine learning"],  # Phải chứa CẢ HAI
        ["deprecated"]                # Không chứa
    ],
    "topic_id": 121,
    "id_mapAlgTypeAI": 23
}]
```

### Test với nhiều topics

```python
"topic": [
    {
        "keywords": [["khoa học"], []],
        "topic_id": 120,
        "id_mapAlgTypeAI": 23
    },
    {
        "keywords": [["công nghệ"], []],
        "topic_id": 121,
        "id_mapAlgTypeAI": 24
    }
]
```

---

## 📊 WORKFLOW CHI TIẾT

```
1. Client gửi payload → Kafka topic_input_ai

2. algo-control (port 6789):
   ✓ Nhận message
   ✓ Kiểm tra is_single = false
   ✓ Forward đến multi-kafka

3. multi-kafka:
   ✓ Gọi app-process (9980) extract documents
   ✓ Lọc văn bản theo keywords:
     • keywords[0]: ["khoa học", "công nghệ"] → Phải chứa
     • keywords[1]: [] → Không loại trừ
   ✓ Kiểm tra văn bản đủ dài
   ✓ Chọn thuật toán từ id_mapAlgTypeAI trong topic

4. Thuật toán (ví dụ: MultiTexRank port 7302):
   ✓ Xử lý tóm tắt multi-document
   ✓ Trả về kết quả

5. Kết quả → Kafka output_topic
```

---

## 🚀 QUICK COMMANDS

```bash
# Xem tất cả containers
docker compose ps

# Restart services nếu cần
docker compose restart multi-kafka m-textrank

# Xem logs realtime
docker compose logs -f multi-kafka m-textrank m-lexrank m-lsa

# Clear Kafka topics (CẨN THẬN!)
docker compose exec kafka-1 kafka-topics.sh \
  --bootstrap-server localhost:9092 \
  --delete --topic output_topic

# Health check
curl http://localhost:9980/  # app-process
curl http://localhost:6789/  # algo-control
```

---

**Tóm tắt**: Sử dụng MultiTexRank (ID=23) vì container có sẵn, test từ bên trong container `multi-kafka`, và kiểm tra kết quả qua Kafka UI hoặc consumer.
