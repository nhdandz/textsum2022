# HƯỚNG DẪN KIỂM TRA THUẬT TOÁN MULTI XỬ LÝ TÓM TẮT THEO CHỦ ĐỀ

## 📋 TỔNG QUAN

Với payload bạn cung cấp:
```json
{
  "topic": [{
    "keywords": [["khoa học", "công nghệ"], []],
    "topic_id": 120,
    "id_mapAlgTypeAI": 17
  }],
  "id_mapAlgTypeAI": [],
  "percent_output": 0.1,
  "is_single": false
}
```

### Thông tin thuật toán:
- **id_mapAlgTypeAI: 17** → **HiMap** (algorId: 17)
- **Loại**: Abstractive (aiId: 3)
- **URL API**: `https://${HOST_IP}:8898/HiMap`
- **Dùng cho**: Văn bản dài (long documents)

---

## 🔍 1. HIỂU WORKFLOW XỬ LÝ TOPIC

```
┌─────────────┐
│   Client    │ Gửi payload với topic
│   Payload   │───────────────────────┐
└─────────────┘                       │
                                      ▼
                        ┌──────────────────────────┐
                        │  Kafka topic_input_ai    │
                        └──────────────────────────┘
                                      │
                                      ▼
                        ┌──────────────────────────┐
                        │  algo-control (6789)     │
                        │  ├─ Kiểm tra is_single   │
                        │  └─ Route đến multi-kafka│
                        └──────────────────────────┘
                                      │
                                      ▼
                        ┌──────────────────────────┐
                        │  multi-kafka consumer    │
                        │  ├─ Extract documents    │
                        │  ├─ Lọc theo keywords:   │
                        │  │  • AND: ["khoa học",  │
                        │  │         "công nghệ"]  │
                        │  │  • NOT: []            │
                        │  ├─ Check văn bản đủ dài │
                        │  └─ Chọn thuật toán #17  │
                        └──────────────────────────┘
                                      │
                                      ▼
                        ┌──────────────────────────┐
                        │  HiMap (8898)            │
                        │  hoặc thuật toán khác    │
                        └──────────────────────────┘
                                      │
                                      ▼
                        ┌──────────────────────────┐
                        │  Kafka output_topic      │
                        │  Trả về kết quả tóm tắt  │
                        └──────────────────────────┘
```

---

## 🎯 2. CÁC THUẬT TOÁN MULTI CÓ THỂ TEST

| ID | Tên thuật toán | Loại | Port | Có sẵn trong hệ thống |
|----|----------------|------|------|----------------------|
| 17 | HiMap | Abstractive | 8898 | ❓ (cần kiểm tra) |
| 19 | MultiBart | Abstractive | 6700 | ❓ (cần kiểm tra) |
| 20 | MultiPeg | Abstractive | 6800 | ❓ (cần kiểm tra) |
| 21 | Primera | Abstractive | 4100 | ❓ (cần kiểm tra) |
| 23 | MultiTexRank | Extractive | 7302 | ✅ Có (m-textrank) |
| 24 | MultiLexRank | Extractive | 7302 | ✅ Có (m-lexrank) |
| 25 | MultiLSA | Extractive | 7302 | ✅ Có (m-lsa) |

**Gợi ý**: Bắt đầu với **MultiTexRank (ID=23)** vì container đang chạy.

---

## 🛠️ 3. CÁCH KIỂM TRA

### Phương pháp 1: Sử dụng Docker exec (Khuyến nghị)

**Bước 1**: Tạo file test payload
```bash
cat > /tmp/test_payload.json << 'EOF'
{
  "user_id": "test_user_multi",
  "sumary_id": "test_multi_topic_120",
  "original_doc_ids": ["doc_001", "doc_002"],
  "documents": [
    {
      "documents_id": "doc_001",
      "raw_text": "VHLDrSB0deG7hyB0aHXhuq10IGFuIHRhb2EgKEFJKSDEkeG6p25nIGPDoWNoIG3huqFuZyBo4bqr YSBs4buJbmggduG7sWMga2hvYSBo4buNYyB24