# Giải pháp cho lỗi "Socket Hang Up" - Tóm tắt ngắn gọn

## 🔴 Vấn đề
- Gửi 1 trang: OK ✅
- Gửi 2+ trang: "socket hang up" ❌

## 🔍 Nguyên nhân chính

### 1. Lỗi syntax trong Flask server (QUAN TRỌNG!)
**File**: `app_process.py` dòng 72

**Lỗi**:
```python
result_doc = list(executor.map(worker, data, timeout=600))  # ❌ SAI!
```
`executor.map()` KHÔNG hỗ trợ tham số `timeout`

**Đã sửa**:
```python
futures = [executor.submit(worker, doc) for doc in data]
result_doc = []
for future in concurrent.futures.as_completed(futures, timeout=600):
    result_doc.append(future.result())
```

### 2. Node.js client không có timeout
**File**: Controller Node.js (file bạn gửi)

**Lỗi**:
```javascript
const configRequest = {
    method: 'post',
    url: `${URL_GET_DOCINFO}/get_content`,
    data: { data: bodyData }
}
let result = await axios(configRequest);  // ❌ Không có timeout!
```

**Cần sửa**:
```javascript
const configRequest = {
    method: 'post',
    url: `${URL_GET_DOCINFO}/get_content`,
    data: { data: bodyData },
    timeout: 600000,  // ✅ 10 phút
    maxContentLength: Infinity,
    maxBodyLength: Infinity
}
```

### 3. Memory leak trong helper.py
File tạm không được dọn dẹp → đã sửa bằng `try-finally`

## ⚡ Cách sửa (2 bước)

### Bước 1: Restart Flask server
```bash
# Kill process cũ
sudo kill -9 $(ps aux | grep "python.*app_process" | grep -v grep | awk '{print $2}')

# Start server mới
cd /home/nhdandz/Documents/tupk/textsum2022/modules/single_kafka
python app_process.py
# Hoặc production mode:
./start_prod.sh
```

### Bước 2: Sửa Node.js client
Thêm 3 dòng vào **2 chỗ** trong controller:

**Chỗ 1**: API `getNumberPage`
```javascript
const configRequest = {
    method: 'post',
    url: `${URL_GET_DOCINFO}/get_number_page`,
    data: { encode: ..., file_type: ... },
    timeout: 120000,        // ← THÊM
    maxContentLength: Infinity,  // ← THÊM
    maxBodyLength: Infinity      // ← THÊM
}
```

**Chỗ 2**: API `getContentPage` (QUAN TRỌNG NHẤT!)
```javascript
const configRequest = {
    method: 'post',
    url: `${URL_GET_DOCINFO}/get_content`,
    data: { data: bodyData },
    timeout: 600000,        // ← THÊM (10 phút)
    maxContentLength: Infinity,  // ← THÊM
    maxBodyLength: Infinity      // ← THÊM
}
```

## ✅ Test sau khi sửa

```bash
cd /home/nhdandz/Documents/tupk/textsum2022/modules/single_kafka
python3 test_2pages.py
```

Nếu thành công → ✅ All tests passed!

## 📄 Chi tiết xem các file:
- `RESTART_SERVER.md` - Hướng dẫn restart server
- `FIX_NODEJS_TIMEOUT.md` - Chi tiết sửa Node.js
- `FIX_TIMEOUT.md` - Giải thích tổng quan

## 🎯 Kết quả mong đợi
Sau khi sửa:
- ✅ Xử lý 1 trang: OK
- ✅ Xử lý 2-10 trang: OK
- ✅ Xử lý 10-50 trang: OK (mất 2-5 phút)
- ✅ Xử lý >50 trang: OK (mất tối đa 10 phút)
