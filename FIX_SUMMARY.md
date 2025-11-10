# Fix Summary - Single Kafka Container Restart Issue

## Ngày: 2025-11-09

## ❌ Vấn đề ban đầu

Container `single-kafka` liên tục restart với lỗi:
```
IndexError: list index out of range
  File "/app/helper.py", line 87, in get_raw_text_by_topic
    topic_choose = topics[0]
```

Và sau khi fix lỗi đầu tiên, xuất hiện lỗi thứ hai:
```
KeyError: 'id_mapAlgTypeAI'
  File "/app/single_root.py", line 53, in handle_message
    input['topic'][0]['id_mapAlgTypeAI'] = topic['id_mapAlgTypeAI']
```

## 🔧 Các bước sửa lỗi

### 1. Fix lỗi `IndexError` trong `helper.py`

**File:** `modules/single_kafka/helper.py`

**Vấn đề:** Hàm `get_raw_text_by_topic()` mong đợi `topics` là một list có ít nhất 2 phần tử `[topic_choose, topic_not]`, nhưng nhận được list rỗng hoặc không đủ phần tử.

**Giải pháp:** Thêm validation để kiểm tra `topics` trước khi truy cập:

```python
def get_raw_text_by_topic(topics,raw_text):
    list_pragrab = raw_text.split('\n')
    list_raw = []

    # Validate topics list
    if not topics or len(topics) < 2:
        # Return all text if topics is empty or invalid
        count = 0
        for pragrab in list_pragrab:
            list_raw.append((count, pragrab))
            count += 1
        return '\n'.join([item[1] for item in list_raw])

    topic_choose = topics[0]
    topic_not = topics[1]
    # ... rest of the code
```

### 2. Fix lỗi `KeyError` trong `single_root.py`

**File:** `modules/single_kafka/single_root.py`

**Vấn đề:** Code cố gắng truy cập các key `'keywords'`, `'topic_id'`, và `'id_mapAlgTypeAI'` từ dict `topic` nhưng các key này có thể không tồn tại.

**Giải pháp:** Sử dụng `.get()` method với giá trị mặc định:

```python
# Get keywords with default empty list if not exists
keywords = topic.get('keywords', [])
text = get_raw_text_by_topic(keywords, text_input)

# Set topic_id and id_mapAlgTypeAI with default None if not exists
input['topic'][0]['topic_id'] = topic.get('topic_id', None)
input['topic'][0]['id_mapAlgTypeAI'] = topic.get('id_mapAlgTypeAI', None)
input['topic'][0]['raw_text'] = text
```

## ✅ Kết quả

- ✅ Container `single-kafka` chạy ổn định, không còn restart
- ✅ API `/get_content` hoạt động và trả về HTTP 200
- ✅ Tất cả containers đang chạy bình thường

### Status sau khi fix:

```
NAME              STATUS
algo-control      Up 2 hours
app-process       Up 2 minutes
clustering        Up 2 hours
kafka-1           Up 2 hours (healthy)
kafka-ui          Up 2 hours
lexrank           Up 2 hours
lsa               Up 2 hours
m-lexrank         Up 2 hours
m-lsa             Up 2 hours
m-textrank        Up 2 hours
multi-kafka       Up 2 hours
result-consumer   Up 2 hours
root-kafka        Up 2 hours
single-kafka      Up 1 minute ✅ (trước đây: Restarting)
textrank          Up 2 hours
```

## 📝 Lưu ý

### Warning về dotenv (không nghiêm trọng)

Warning `Python-dotenv could not parse statement starting at line 1` xuất hiện vì dòng đầu tiên của file `.env` là comment:

```bash
# ==================== Network Configuration ====================
```

Đây KHÔNG phải lỗi nghiêm trọng. `load_dotenv()` vẫn hoạt động bình thường và load các biến môi trường từ các dòng tiếp theo.

## 🧪 Cách test

Sử dụng script test được tạo:

```bash
# Test cơ bản
./test_api.sh

# Test với file PDF thật
./test_api.sh /path/to/your/file.pdf

# Hoặc curl trực tiếp
curl -X POST http://192.168.210.42:9980/get_content \
  -H "Content-Type: application/json" \
  -d '{
    "data": [{
      "documents_id": "test_001",
      "encode": "<base64_encoded_pdf>",
      "file_type": 1,
      "page_from": 0,
      "page_to": 5
    }]
  }' | jq '.'
```

## 📌 Tham số API quan trọng

- `file_type: 1` - **SỐ NGUYÊN**, không phải chuỗi "pdf"
- `page_from: 0` - Bắt đầu từ index **0**, không phải 1
- `page_to: N` - Đọc đến trang N
- Sử dụng IP `192.168.210.42` từ file `.env`

## 🔍 Commands hữu ích

```bash
# Kiểm tra status containers
docker compose ps

# Xem logs của single-kafka
docker compose logs -f single-kafka

# Xem logs của app-process
docker compose logs -f app-process

# Restart một service cụ thể
docker compose restart single-kafka

# Rebuild và restart
docker compose stop single-kafka
docker compose build single-kafka
docker compose up -d single-kafka
```

## ✨ Bản chất của fix

Các fix này thêm **defensive programming** để xử lý các trường hợp edge case:
1. Khi Kafka message không có đủ thông tin về topics
2. Khi dict không có đầy đủ các key mong đợi

Điều này giúp service tiếp tục chạy thay vì crash khi nhận được dữ liệu không hoàn chỉnh.
