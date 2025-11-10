# Hướng dẫn Restart Flask Server

## Đã sửa lỗi quan trọng!

**Lỗi**: Dòng 72 trong `app_process.py` có syntax sai - `executor.map()` không hỗ trợ tham số `timeout`.

**Đã sửa**: Dùng `executor.submit()` và `as_completed()` thay thế.

## Cách restart server

### Option 1: Docker (nếu đang dùng Docker)
```bash
# Stop và xóa container cũ
docker stop app-process
docker rm app-process

# Build lại image
cd /home/nhdandz/Documents/tupk/textsum2022/modules/single_kafka
docker build -t app-process .

# Run container mới
docker run -d -p 9980:9980 --name app-process app-process
```

### Option 2: Kill process thủ công
```bash
# Tìm process ID
ps aux | grep "python.*app_process" | grep -v grep

# Kill process (cần sudo vì process chạy bằng root)
sudo kill -9 <PID1> <PID2>

# Ví dụ:
sudo kill -9 56122 270838

# Start lại server
cd /home/nhdandz/Documents/tupk/textsum2022/modules/single_kafka
python app_process.py
# Hoặc với Gunicorn (production):
./start_prod.sh
```

### Option 3: Systemd service (nếu có)
```bash
sudo systemctl restart app-process
# Hoặc
sudo systemctl restart flask-app
```

## Sau khi restart, test lại:

```bash
cd /home/nhdandz/Documents/tupk/textsum2022/modules/single_kafka
python3 test_2pages.py
```

Nếu thành công, bạn sẽ thấy:
```
File size: 95650 bytes
Base64 size: 127536 chars

=== Test 1: Get number of pages ===
Status: 200
Response: {'number_page': 4}

=== Test 2: Get content - 1 page (page 0-0) ===
Status: 200
Response message: OK
Text length: ...

=== Test 3: Get content - 2 pages (page 0-1) ===
Status: 200
Response message: OK
Text length: ...

✓ All tests passed!
```

## Các file đã sửa:

1. **app_process.py** (dòng 66-96): Sửa lỗi timeout syntax
2. **helper.py**: Thêm try-finally để clean up file tạm
3. **gunicorn_config.py**: Cấu hình timeout 600s
4. **Dockerfile**: Dùng Gunicorn thay vì Flask dev server
5. **requirements.txt**: Thêm gunicorn

## Sau khi Flask server hoạt động, sửa Node.js client:

Xem file `FIX_NODEJS_TIMEOUT.md` để biết cách thêm timeout vào axios requests.

**TÓM TẮT**: Thêm vào mỗi axios request:
```javascript
const configRequest = {
    method: 'post',
    url: `${URL_GET_DOCINFO}/get_content`,
    data: { data: bodyData },
    timeout: 600000,          // ← THÊM DÒNG NÀY (10 phút)
    maxContentLength: Infinity,  // ← THÊM DÒNG NÀY
    maxBodyLength: Infinity      // ← THÊM DÒNG NÀY
}
```
