# Khắc phục lỗi "socket hang up" khi xử lý nhiều trang

## Vấn đề
Khi gửi request từ trang 1 đến trang lớn hơn (nhiều trang), server bị lỗi "socket hang up" vì:
1. Request timeout - xử lý lâu quá
2. File tạm không được giải phóng kịp thời
3. Flask development server không xử lý tốt các request dài

## Các thay đổi đã thực hiện

### 1. Fix memory leak trong helper.py
- Thêm `try-finally` block để đảm bảo file tạm được đóng và xóa
- Thêm `doc.close()` cho PyMuPDF documents
- Files: `helper.py` (dòng 21-44, 56-93)

### 2. Tăng timeout và worker threads trong app_process.py
- Tăng ThreadPoolExecutor từ 10 lên 20 workers
- Thêm timeout 10 phút cho mỗi task
- Cải thiện error handling và logging
- Files: `app_process.py` (dòng 54-86)

### 3. Thêm Gunicorn production server
- Tạo file cấu hình Gunicorn với timeout 600 giây (10 phút)
- Cập nhật Dockerfile để sử dụng Gunicorn
- Files: `gunicorn_config.py`, `Dockerfile`, `requirements.txt`

## Cách chạy

### Option 1: Development mode (Flask built-in server)
```bash
./start_dev.sh
# hoặc
python app_process.py
```

### Option 2: Production mode (Gunicorn - KHUYẾN NGHỊ)
```bash
./start_prod.sh
# hoặc
gunicorn --config gunicorn_config.py app_process:app
```

### Option 3: Docker
```bash
# Build image
docker build -t app-process .

# Run container với Gunicorn (mặc định)
docker run -p 9980:9980 app-process

# Hoặc run với Flask development server
docker run -p 9980:9980 app-process python app_process.py
```

## Các cải tiến khác

### Tăng hiệu suất xử lý
- Tăng số worker threads từ 10 → 20
- Xử lý song song nhiều document hơn

### Cải thiện logging
- Log chi tiết các lỗi với stack trace
- Log thời gian xử lý
- Thông báo lỗi rõ ràng hơn

### Resource management
- Tự động dọn dẹp file tạm
- Đóng file handles đúng cách
- Tránh memory leak

## Kiểm tra

### Test với 1 trang (nên chạy nhanh)
```bash
curl -X POST http://192.168.210.42:9980/get_content \
  -H "Content-Type: application/json" \
  -d '{"data":[{"encode":"base64_string","file_type":1,"page_from":0,"page_to":0,"documents_id":"doc1"}]}'
```

### Test với nhiều trang
```bash
curl -X POST http://192.168.210.42:9980/get_content \
  -H "Content-Type: application/json" \
  -d '{"data":[{"encode":"base64_string","file_type":1,"page_from":0,"page_to":50,"documents_id":"doc1"}]}'
```

## Nếu vẫn gặp vấn đề

### 1. Kiểm tra client timeout
Đảm bảo client (Node.js, axios, etc.) có timeout đủ lớn:
```javascript
axios.post(url, data, {
  timeout: 600000 // 10 phút
})
```

### 2. Kiểm tra reverse proxy timeout (nếu có)
Nếu dùng Nginx/Apache, cần tăng timeout:
```nginx
# Nginx
proxy_read_timeout 600s;
proxy_connect_timeout 600s;
proxy_send_timeout 600s;
```

### 3. Tăng timeout trong gunicorn_config.py
Nếu cần xử lý file rất lớn, tăng timeout:
```python
timeout = 1200  # 20 phút
```

### 4. Kiểm tra resource (RAM, CPU)
```bash
# Xem memory usage
free -h

# Xem CPU usage
top

# Xem disk space
df -h
```

## Lưu ý quan trọng

1. **Timeout mặc định**: 10 phút (600 giây)
2. **Max workers**: 20 threads
3. **Gunicorn workers**: CPU cores * 2 + 1
4. **Production**: Luôn dùng Gunicorn, không dùng Flask development server

## Troubleshooting

### Lỗi "No module named 'gunicorn'"
```bash
pip install gunicorn==21.2.0
```

### Lỗi memory khi xử lý file lớn
- Giảm số workers trong gunicorn_config.py
- Tăng RAM cho container/server

### Request vẫn bị timeout
- Kiểm tra client timeout settings
- Kiểm tra reverse proxy timeout
- Tăng timeout trong gunicorn_config.py
