# TÓM TẮT: KIỂM TRA THUẬT TOÁN MULTI VỚI TOPIC

## 🎯 PAYLOAD CỦA BẠN

```json
{
  "topic": [{
    "keywords": [["khoa học", "công nghệ"], []],
    "topic_id": 120,
    "id_mapAlgTypeAI": 17  // HiMap
  }],
  "percent_output": 0.1,
  "is_single": false
}
```

## 🔍 PHÂN TÍCH

- **id_mapAlgTypeAI: 17** → **HiMap** (Abstractive, port 8898)
- **Lọc văn bản**: Phải chứa BOTH "khoa học" AND "công nghệ"
- **Tóm tắt**: 10% độ dài (percent_output = 0.1)
- **Loại**: Multi-document (is_single = false)

## ⚡ TEST NHANH (3 BƯỚC)

### 1. Vào container
```bash
docker compose exec multi-kafka bash
```

### 2. Chạy test
```bash
python3 << 'EOF'
from kafka import KafkaProducer
import json, base64

text = "Trí tuệ nhân tạo và công nghệ đang cách mạng khoa học hiện đại"
encoded = base64.b64encode(text.encode()).decode()

producer = KafkaProducer(
    bootstrap_servers=['kafka-1:9092'],
    value_serializer=lambda x: json.dumps(x).encode('utf-8')
)

payload = {
    "user_id": "test", "sumary_id": "test123",
    "original_doc_ids": ["d1"], "documents": [{
        "documents_id": "d1", "raw_text": encoded,
        "file_type": 0, "page_from": 0, "page_to": 9999
    }],
    "topic": [{"keywords": [["khoa học", "công nghệ"], []],
               "topic_id": 120, "id_mapAlgTypeAI": 23}],
    "id_mapAlgTypeAI": [], "percent_output": 0.1, "is_single": False
}

producer.send('topic_input_ai', payload).get(timeout=10)
print(f"✅ Sent! sumary_id: {payload['sumary_id']}")
producer.close()
EOF
```

### 3. Xem kết quả
```bash
# Xem logs
docker compose logs -f multi-kafka m-textrank

# Hoặc Kafka UI
# http://localhost:8080 → Topic: output_topic
```

## 📋 THUẬT TOÁN CÓ SẴN

| ID | Tên | Container | Trạng thái |
|----|-----|-----------|------------|
| 23 | MultiTexRank | m-textrank | ✅ Running |
| 24 | MultiLexRank | m-lexrank | ✅ Running |
| 25 | MultiLSA | m-lsa | ✅ Running |
| 17 | HiMap | ❓ | ❓ Cần check |

**Gợi ý**: Dùng ID=23 (MultiTexRank) vì container đã chạy

## 📖 TÀI LIỆU CHI TIẾT

- [TEST_MULTI_TOPIC_GUIDE.md](./TEST_MULTI_TOPIC_GUIDE.md) - Hướng dẫn đầy đủ
- [test_multi_topic_kafka.py](./test_multi_topic_kafka.py) - Script Python test
- [check_kafka_output.py](./check_kafka_output.py) - Script kiểm tra kết quả

## 🐛 DEBUG

```bash
# Services status
docker compose ps

# Logs
docker compose logs -f multi-kafka
docker compose logs -f m-textrank m-lexrank m-lsa

# Health check
curl http://localhost:9980/  # app-process: ✅ OK
curl http://localhost:6789/  # algo-control: ✅ OK
```

## 💡 TIPS

1. **Văn bản phải đủ dài**: Sau khi lọc theo keywords phải > 800 từ
2. **Test với MultiTexRank trước**: Container đã có sẵn
3. **Xem Kafka UI**: http://localhost:8080 để debug
4. **Check logs realtime**: `docker compose logs -f multi-kafka`

## ❓ HỎI ĐÁP

**Q: Tại sao không nhận được kết quả?**
- A: Kiểm tra logs: `docker compose logs multi-kafka | grep -i error`

**Q: Làm sao biết thuật toán nào có sẵn?**
- A: `docker compose ps | grep "Up"`

**Q: Keywords hoạt động như thế nào?**
- A: `keywords[0]` = AND (phải chứa tất cả), `keywords[1]` = NOT (loại trừ)

---

**🚀 Bắt đầu ngay**: Sao chép 3 bước trên và chạy!
