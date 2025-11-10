# Sửa lỗi Socket Hang Up ở Node.js Client

## Vấn đề
Axios trong Node.js **không có timeout mặc định** hoặc có timeout rất ngắn. Khi Flask server xử lý lâu (>2 phút), socket bị đóng và báo lỗi "socket hang up".

## Nguyên nhân
```javascript
const configRequest = {
    method: 'post',
    url: `${URL_GET_DOCINFO}/get_content`,
    data: { data: bodyData }
}
let result = await axios(configRequest);  // ❌ KHÔNG CÓ TIMEOUT!
```

## Giải pháp

### Cách 1: Thêm timeout vào từng request (KHUYẾN NGHỊ)

Sửa 2 API sau trong controller của bạn:

#### 1. API `getNumberPage`
```javascript
getNumberPage: async (req, res) => {
    try {
        const { documentId } = req.body
        const documentInfo = await documents.findOne({
            where: { documentId: documentId },
            include: {
                model: typeOfFile,
                as: "typeOfFile",
            }
        })

        if (documentInfo) {
            var file_type = 0
            if (documentInfo.typeOfFile.displayName === '.pdf') {
                file_type = 1
            } else if (documentInfo.typeOfFile.displayName === '.docx') {
                file_type = 2
            } else {
                file_type = 3
            }

            const bitmap = fs.readFileSync(`${USER_UPLOAD_DOCS}/${documentInfo.ownerId}/${documentId}${documentInfo.typeOfFile.displayName}`);

            const configRequest = {
                method: 'post',
                url: `${URL_GET_DOCINFO}/get_number_page`,
                data: {
                    encode: new Buffer.from(bitmap).toString('base64'),
                    file_type: file_type
                },
                timeout: 120000,  // ✅ THÊM: 2 phút timeout
                maxContentLength: Infinity,  // ✅ THÊM: Không giới hạn response size
                maxBodyLength: Infinity      // ✅ THÊM: Không giới hạn request size
            }

            let result = await axios(configRequest)
            return res.send(onSuccess({
                number_page: result.data.number_page
            }));
        }
        return res.send(onError(404, "Không tìm thấy thông tin văn bản"));
    } catch (error) {
        console.error('Error in getNumberPage:', error.message);
        return res.send(onError(500, error));
    }
},
```

#### 2. API `getContentPage` (QUAN TRỌNG NHẤT!)
```javascript
getContentPage: async (req, res) => {
    try {
        const { inListDocument, page_from = 1, page_to = 9999, singleSumary } = req.body
        const listDocumentInfo = await documents.findAll({
            where: {
                documentId: { [Op.in]: inListDocument }
            },
            include: {
                model: typeOfFile,
                as: "typeOfFile",
            },
        })

        let bodyData = []
        for (let index = 0; index < listDocumentInfo.length; index++) {
            const documentInfo = listDocumentInfo[index];
            var file_type = 0
            if (documentInfo.typeOfFile.displayName === '.pdf') {
                file_type = 1
            } else if (documentInfo.typeOfFile.displayName === '.docx') {
                file_type = 2
            } else {
                file_type = 3
            }

            const bitmap = fs.readFileSync(`${USER_UPLOAD_DOCS}/${documentInfo.ownerId}/${documentInfo.documentId}${documentInfo.typeOfFile.displayName}`);
            bodyData.push({
                documents_id: documentInfo.documentId,
                encode: new Buffer.from(bitmap).toString('base64'),
                file_type: file_type,
                page_from: page_from - 1,
                page_to: page_to - 1
            })
        }

        const configRequest = {
            method: 'post',
            url: `${URL_GET_DOCINFO}/get_content`,
            data: { data: bodyData },
            timeout: 600000,  // ✅ THÊM: 10 phút timeout (600 giây)
            maxContentLength: Infinity,  // ✅ THÊM: Không giới hạn response size
            maxBodyLength: Infinity      // ✅ THÊM: Không giới hạn request size
        }

        // Gọi API với error handling tốt hơn
        let result = await axios(configRequest);

        // Cập nhật content cho các document
        if (result.data?.result && Array.isArray(result.data?.result)) {
            if (!singleSumary) {
                for (let index = 0; index < result.data?.result.length; index++) {
                    const element = result.data?.result[index];
                    const documentInfo = await documents.findOne({
                        where: { documentId: element.documents_id }
                    })
                    if (documentInfo) {
                        documentInfo.content = element.text
                        await documentInfo.save()
                    }
                }
            }
            return res.send(onSuccess(result.data?.result));
        }
        return res.send(onError(404, 'Not found'));
    } catch (error) {
        console.error('Error in getContentPage:', error.message);
        if (error.code === 'ECONNABORTED') {
            return res.send(onError(408, 'Request timeout - File quá lớn hoặc xử lý lâu'));
        }
        return res.send(onError(500, error.message));
    }
},
```

### Cách 2: Tạo axios instance với default config (TỐT HƠN)

Tạo file `utils/axiosConfig.js`:

```javascript
const axios = require('axios');

// Tạo axios instance với config mặc định
const axiosInstance = axios.create({
    timeout: 600000,  // 10 phút mặc định
    maxContentLength: Infinity,
    maxBodyLength: Infinity,
    headers: {
        'Content-Type': 'application/json'
    }
});

// Thêm interceptor để log lỗi
axiosInstance.interceptors.response.use(
    response => response,
    error => {
        if (error.code === 'ECONNABORTED') {
            console.error('Request timeout:', error.config.url);
        } else if (error.response) {
            console.error('Response error:', error.response.status, error.response.data);
        } else if (error.request) {
            console.error('No response received:', error.message);
        } else {
            console.error('Request setup error:', error.message);
        }
        return Promise.reject(error);
    }
);

module.exports = axiosInstance;
```

Sau đó trong controller, thay:
```javascript
const axios = require('axios');
```

Bằng:
```javascript
const axios = require('../utils/axiosConfig');  // Dùng custom axios instance
```

### Cách 3: Tăng timeout cho toàn bộ Express server

Trong file khởi tạo Express server (thường là `app.js` hoặc `server.js`):

```javascript
const express = require('express');
const app = express();

// Tăng timeout cho server
const server = app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});

// Tăng timeout lên 15 phút
server.timeout = 900000;  // 15 phút
server.keepAliveTimeout = 900000;
server.headersTimeout = 910000;  // Phải lớn hơn keepAliveTimeout
```

## Kiểm tra

### Test với Python script
```bash
cd /home/nhdandz/Documents/tupk/textsum2022/modules/single_kafka
python test_2pages.py
```

### Test với curl
```bash
# Test 1 trang
curl -X POST http://192.168.210.42:9980/get_content \
  -H "Content-Type: application/json" \
  -d '{"data":[{"documents_id":"test","encode":"...base64...","file_type":1,"page_from":0,"page_to":0}]}' \
  --max-time 120

# Test 2 trang
curl -X POST http://192.168.210.42:9980/get_content \
  -H "Content-Type: application/json" \
  -d '{"data":[{"documents_id":"test","encode":"...base64...","file_type":1,"page_from":0,"page_to":1}]}' \
  --max-time 120
```

## Các tham số timeout quan trọng

### Axios timeout
- `timeout`: Tổng thời gian chờ response (ms)
- `maxContentLength`: Kích thước response tối đa (bytes)
- `maxBodyLength`: Kích thước request body tối đa (bytes)

### Express/Node.js timeout
- `server.timeout`: Thời gian timeout của request (ms)
- `server.keepAliveTimeout`: Thời gian giữ kết nối (ms)
- `server.headersTimeout`: Thời gian chờ headers (ms)

### Gunicorn timeout (Flask server)
- Đã cấu hình trong `gunicorn_config.py`: `timeout = 600` (10 phút)

## Khuyến nghị

1. **Dùng Cách 2** - Tạo axios instance với config mặc định
2. **Timeout nên là**:
   - 1-10 trang: 120 giây (2 phút)
   - 10-50 trang: 300 giây (5 phút)
   - >50 trang: 600 giây (10 phút)
3. **Thêm retry logic** cho các request timeout
4. **Log chi tiết** để debug

## Troubleshooting

### Vẫn bị "socket hang up"?
1. Kiểm tra Flask server có chạy không: `ps aux | grep app_process`
2. Kiểm tra Flask server logs
3. Test trực tiếp với curl
4. Kiểm tra firewall/proxy timeout

### Response quá lớn?
- Tăng `maxContentLength` và `maxBodyLength`
- Kiểm tra Express body-parser limits:
```javascript
app.use(express.json({ limit: '50mb' }));
app.use(express.urlencoded({ limit: '50mb', extended: true }));
```

### Vẫn chậm?
- Tối ưu Flask server (đã làm)
- Xem xét xử lý batch nhỏ hơn
- Dùng pagination/streaming
