# Hướng dẫn cấu hình khi chuyển máy

Khi chuyển sang máy mới, bạn chỉ cần sửa file `.env` duy nhất ở thư mục root:

## 1. Cập nhật IP máy mới

```bash
# Xem IP hiện tại
hostname -I

# Sửa file .env
nano .env
```

## 2. Các biến cần sửa

Thay tất cả `192.168.213.13` thành IP máy mới của bạn:

```env
HOST_IP=<IP_MÁY_MỚI>
BACKEND_API_URL=http://<IP_MÁY_MỚI>:8000/api/result
OLLAMA_URL=http://<IP_MÁY_MỚI>:11434
MONGO_HOST=<IP_MÁY_MỚI>
```

## 3. Rebuild và restart services

```bash
docker compose build
docker compose down
docker compose up -d
```

## Lưu ý

- **KHÔNG CẦN** sửa file `.env` trong các thư mục modules
- Tất cả modules đã được cấu hình đọc từ file `.env` chính
- File `.env.local` trong modules chỉ là backup, không được sử dụng
