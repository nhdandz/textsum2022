# FIX: FRONTEND HIỂN THỊ "ĐANG TÓM TẮT" MẶC DÙ ĐÃ XONG

## ⚠️ VẤN ĐỀ

Frontend vẫn hiển thị "đang tóm tắt" mặc dù:
- ✅ Thuật toán đã xử lý xong
- ✅ Kết quả đã có trong Kafka `result_ai` topic
- ❌ Frontend KHÔNG nhận được kết quả

## 🔍 NGUYÊN NHÂN

### Luồng trả kết quả:

```
THUẬT TOÁN (m-lexrank, etc.)
└─ Xử lý xong → Gửi kết quả

        ↓

KAFKA result_ai topic  ✅ OK
└─ Chứa kết quả tóm tắt

        ↓

result-consumer container  ✅ Đọc được
├─ Đọc từ result_ai
└─ Gửi HTTP POST đến BACKEND_API_URL

        ↓

BACKEND_API_URL  ❌ SAI CONFIG
├─ Config: http://192.168.210.42:8000/api/result
└─ ERROR: Connection refused (Port 8000 không chạy!)

        ↓

BACKEND THẬT SỰ (Port 5002)  ❌ KHÔNG NHẬN ĐƯỢC
├─ Đang chạy tại: http://192.168.210.42:5002
└─ Không nhận được kết quả từ result-consumer

        ↓

FRONTEND  ❌ STUCK
└─ Poll backend nhưng không có data
```

### Logs chứng minh:

```bash
$ docker compose logs result-consumer

✅ INFO: Received result message: sumary_id: 306, 307, 308...

❌ ERROR: Connection refused to http://192.168.210.42:8000/api/result
   HTTPConnectionPool(host='192.168.210.42', port=8000):
   Failed to establish a new connection: [Errno 111] Connection refused
```

**Kết luận**:
- Port 8000: KHÔNG CHẠY ❌
- Port 5002: Backend thật đang chạy ✅
- `BACKEND_API_URL` config SAI PORT!

---

## ✅ GIẢI PHÁP

### Giải pháp 1: Sửa BACKEND_API_URL (Khuyến nghị ⭐)

#### Bước 1: Tìm API endpoint đúng của backend

```bash
# Test các endpoints có thể
curl -X POST http://192.168.210.42:5002/api/result \
  -H "Content-Type: application/json" \
  -d '{"sumary_id": 306, "test": true}'

# Hoặc
curl -X POST http://192.168.210.42:5002/api/multisum/result \
  -H "Content-Type: application/json" \
  -d '{"sumary_id": 306, "test": true}'
```

#### Bước 2: Sửa file `.env`

```bash
# Sửa dòng này
# BACKEND_API_URL=http://192.168.210.42:8000/api/result

# Thành (sau khi biết endpoint đúng)
BACKEND_API_URL=http://192.168.210.42:5002/api/multisum/result
# HOẶC
BACKEND_API_URL=http://192.168.210.42:5002/api/result
```

#### Bước 3: Restart result-consumer

```bash
docker compose restart result-consumer
```

#### Bước 4: Xem logs để kiểm tra

```bash
docker compose logs -f result-consumer

# Nếu thành công, sẽ thấy:
# ✅ INFO: Successfully sent result for summary_id: 306
```

---

### Giải pháp 2: Tạo API endpoint mới (Nếu backend không có)

Nếu backend (port 5002) chưa có endpoint để nhận kết quả:

#### File: `backend/routes/result.js` (hoặc tương tự)

```javascript
// POST /api/result
router.post('/result', async (req, res) => {
    try {
        const { sumary_id, user_id, result } = req.body;

        // Lưu vào database
        await db.updateSummaryResult(sumary_id, {
            result: result,
            status: 'completed',
            completed_at: new Date()
        });

        // Notify frontend qua WebSocket (nếu có)
        io.to(`user_${user_id}`).emit('summary_complete', {
            sumary_id,
            result
        });

        res.json({ success: true });
    } catch (error) {
        console.error('Error saving result:', error);
        res.status(500).json({ error: error.message });
    }
});
```

---

### Giải pháp 3: Workaround - Đọc trực tiếp từ Kafka (Tạm thời)

Nếu không sửa được backend ngay, tạo script đọc từ Kafka:

#### File: `read_result_direct.py`

```python
#!/usr/bin/env python3
from kafka import KafkaConsumer
import json

consumer = KafkaConsumer(
    'result_ai',
    bootstrap_servers=['localhost:9092'],
    auto_offset_reset='latest',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

print("Listening for results...")
for msg in consumer:
    data = msg.value
    print(f"\n✅ Kết quả cho sumary_id: {data.get('sumary_id')}")
    print(json.dumps(data, indent=2, ensure_ascii=False))
```

```bash
python3 read_result_direct.py
```

---

## 🔧 DEBUG & VERIFICATION

### 1. Kiểm tra backend có chạy không

```bash
# Backend thật (port 5002)
curl http://192.168.210.42:5002/api/multisum/status

# Nếu có response → Backend đang chạy ✅
```

### 2. Kiểm tra result-consumer logs

```bash
docker compose logs result-consumer | grep "sumary_id: 306"

# Nếu thấy:
# ✅ "Received result message" → Consumer nhận được
# ❌ "Connection refused" → Backend không chạy hoặc URL sai
```

### 3. Test gửi result thủ công

```bash
# Lấy message từ Kafka
docker compose exec kafka-1 kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 \
  --topic result_ai \
  --from-beginning \
  --max-messages 1 > result_sample.json

# Gửi thủ công đến backend
curl -X POST http://192.168.210.42:5002/api/result \
  -H "Content-Type: application/json" \
  -d @result_sample.json
```

### 4. Kiểm tra frontend có poll không

```bash
# Xem network tab trong browser
# Tìm request đến: /api/multisum/status/{sumary_id}
# Nếu status = 2 (completed) → OK
# Nếu status = 1 (processing) → Chưa nhận được kết quả
```

---

## 📊 BẢNG PORTS & SERVICES

| Port | Service | Status | Mục đích |
|------|---------|--------|----------|
| 8000 | ❌ KHÔNG TỒN TẠI | Down | BACKEND_API_URL (config sai) |
| 5002 | ✅ Backend Web | Running | API thật, frontend gọi đến đây |
| 9092 | ✅ Kafka | Running | Message broker |
| 6789 | ✅ algo-control | Running | Routing thuật toán |
| 9980 | ✅ app-process | Running | Extract documents |

---

## 🎯 ACTION PLAN

### Ngắn hạn (Fix ngay - 5 phút)

1. ✅ Xác định vấn đề: Port 8000 không chạy
2. ⬜ Tìm API endpoint đúng của backend (port 5002)
3. ⬜ Sửa `BACKEND_API_URL` trong `.env`
4. ⬜ Restart result-consumer
5. ⬜ Test với sumary_id mới

### Dài hạn (Cải thiện hệ thống)

1. ⬜ Thêm health check cho backend API
2. ⬜ Thêm retry logic trong result-consumer
3. ⬜ Thêm logging chi tiết hơn
4. ⬜ Thêm monitoring/alerting
5. ⬜ Sử dụng WebSocket để notify frontend realtime

---

## 💡 TIPS

### Tip 1: Kiểm tra backend endpoints

```bash
# List all routes trong backend
# (Tùy framework: Express, Flask, FastAPI...)

# Express.js
node -e "const app = require('./app'); app._router.stack.forEach(r => console.log(r.route?.path))"

# Flask
flask routes

# FastAPI
# Mở http://localhost:5002/docs
```

### Tip 2: Thêm logging vào backend

```javascript
// Trong backend API
app.use((req, res, next) => {
    console.log(`${req.method} ${req.path}`, req.body);
    next();
});
```

### Tip 3: Monitor Kafka topic

```bash
# Watch result_ai topic realtime
docker compose exec kafka-1 kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 \
  --topic result_ai \
  --from-beginning | jq '.sumary_id'
```

---

## ❓ FAQ

**Q: Tại sao không dùng port 8000?**
- A: Port 8000 có thể là config cũ hoặc development. Backend production chạy ở 5002.

**Q: Làm sao biết endpoint đúng?**
- A:
  1. Xem backend source code
  2. Xem API documentation
  3. Test các endpoints phổ biến: `/api/result`, `/api/multisum/result`

**Q: Có cần restart tất cả services không?**
- A: Không. Chỉ cần restart `result-consumer` sau khi sửa config.

**Q: Nếu vẫn không work?**
- A: Kiểm tra:
  1. Backend logs: `tail -f backend.log`
  2. Firewall: `sudo ufw status`
  3. Network: `ping 192.168.210.42`

---

## 🚀 QUICK FIX

```bash
# 1. Tìm endpoint đúng (thử từng cái)
curl -X POST http://192.168.210.42:5002/api/result -d '{"test":true}'
curl -X POST http://192.168.210.42:5002/api/multisum/result -d '{"test":true}'

# 2. Sửa .env
nano .env
# Sửa BACKEND_API_URL thành endpoint đúng

# 3. Restart
docker compose restart result-consumer

# 4. Check logs
docker compose logs -f result-consumer
```

---

**TÓM TẮT**: Port 8000 không chạy, backend thật ở port 5002. Sửa `BACKEND_API_URL` trong `.env` và restart `result-consumer`. 🎯
