# Hướng dẫn cấu hình Environment Variables

## Tổng quan

Project này đã được cấu hình để sử dụng biến môi trường thay vì IP tĩnh. Tất cả các IP trong hệ thống sẽ được load từ file `.env`.

## Cấu trúc

```
textsum2022/
├── .env                    # File chứa cấu hình IP (QUAN TRỌNG!)
├── env_config.py          # Helper để load env trong Python
├── json_env_loader.py     # Helper để load JSON với env vars
├── replace_ips_simple.py  # Script thay thế IP tĩnh
└── docker-compose.yml     # Docker compose với env_file
```

## Cách sử dụng

### 1. Cấu hình IP trong file .env

Mở file `.env` và thay đổi `HOST_IP` thành IP của máy bạn:

```bash
# Sử dụng localhost (chạy trên cùng máy)
HOST_IP=127.0.0.1

# Hoặc sử dụng IP của máy trong mạng
HOST_IP=192.168.1.100

# Hoặc giữ nguyên IP hiện tại
HOST_IP=192.168.210.42
```

### 2. Thay thế tất cả IP tĩnh trong code

Chạy script để thay thế tất cả IP tĩnh bằng placeholder `${HOST_IP}`:

```bash
python3 replace_ips_simple.py
```

Script này sẽ:
- Tìm tất cả file `.py`, `.json`, `.yaml`, `.yml`, `.txt`
- Thay thế `192.168.210.42` → `${HOST_IP}`
- Thay thế `192.168.2.25` → `${HOST_IP}`

### 3. Sử dụng trong Python code

#### Cách 1: Dùng os.getenv() trực tiếp

```python
import os
from dotenv import load_dotenv

load_dotenv()

host_ip = os.getenv('HOST_IP', '192.168.210.42')
kafka_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', f'{host_ip}:9092')
```

#### Cách 2: Dùng env_config.py (Khuyên dùng)

```python
from env_config import HOST_IP, KAFKA_BOOTSTRAP_SERVERS, get_service_url

# Sử dụng trực tiếp
bootstrap_servers = [KAFKA_BOOTSTRAP_SERVERS]

# Hoặc lấy URL của service
textrank_url = get_service_url('textrank')  # http://{HOST_IP}:7300/TexRank
```

### 4. Load JSON files với env variables

Các file JSON (như `algo.json`, `configs.json`) có thể chứa `${HOST_IP}`:

```json
{
  "urlAPI": "http://${HOST_IP}:7300/TexRank"
}
```

Để load chúng:

```python
from json_env_loader import load_json_with_env, load_json_list_with_env

# Load single JSON file
config = load_json_with_env('configs.json')

# Load JSONL file (multiple JSON objects per line)
algos = load_json_list_with_env('algo.json')
```

### 5. Chạy Docker Compose

Docker Compose đã được cấu hình để tự động load file `.env`:

```bash
# Chạy tất cả services
docker-compose up -d

# Hoặc chạy services cụ thể
docker-compose up -d kafka zookeeper

# Kiểm tra logs
docker-compose logs -f
```

Mỗi service trong `docker-compose.yml` đã có:
```yaml
env_file:
  - .env
```

## Các biến môi trường có sẵn

File `.env` chứa các biến sau:

| Biến | Mặc định | Mô tả |
|------|----------|-------|
| `HOST_IP` | 192.168.210.42 | IP của máy host |
| `KAFKA_BOOTSTRAP_SERVERS` | ${HOST_IP}:9092 | Kafka server |
| `ALGO_CONTROL_URL` | http://${HOST_IP}:6789 | Algorithm control API |
| `APP_PROCESS_URL` | http://${HOST_IP}:9980 | App process API |
| `STATUS_WEB_URL` | http://${HOST_IP}:5002/... | Status web API |
| `CLUSTERING_URL` | http://${HOST_IP}:9400/... | Text clustering API |
| ... | ... | Xem thêm trong `.env` |

## Troubleshooting

### Lỗi: Connection refused

```bash
# Kiểm tra IP của bạn
hostname -I

# Cập nhật HOST_IP trong .env
echo "HOST_IP=192.168.1.100" > .env
```

### JSON không parse được với ${HOST_IP}

Sử dụng `json_env_loader.py`:

```python
# ĐÚNG ✓
from json_env_loader import load_json_with_env
data = load_json_with_env('config.json')

# SAI ✗
import json
with open('config.json') as f:
    data = json.load(f)  # Sẽ lỗi vì ${HOST_IP} không phải JSON hợp lệ
```

### Docker container không kết nối được với nhau

Trong Docker network, các container nên dùng service name thay vì IP:

```python
# Trong container, dùng service name
KAFKA_BOOTSTRAP_SERVERS = 'kafka:9092'  # ĐÚNG

# Ngoài container, dùng HOST_IP
KAFKA_BOOTSTRAP_SERVERS = '192.168.210.42:9092'  # ĐÚNG
```

## Best Practices

1. **Không commit IP thật vào git**: Luôn dùng placeholder trong code
2. **Copy .env cho từng môi trường**: Tạo `.env.development`, `.env.production`
3. **Dùng env_config.py**: Tập trung quản lý config ở một nơi
4. **Test sau khi thay đổi**: Chạy `replace_ips_simple.py` và test kỹ

## Ví dụ cấu hình cho các môi trường khác nhau

### Development (localhost)
```bash
HOST_IP=127.0.0.1
```

### Testing (local network)
```bash
HOST_IP=192.168.1.100
```

### Production
```bash
HOST_IP=10.0.0.50
```

## Câu hỏi thường gặp

**Q: Tôi có cần chạy `replace_ips_simple.py` nhiều lần không?**

A: Chỉ cần chạy 1 lần sau khi thiết lập. Nếu thêm code mới có IP tĩnh, chạy lại.

**Q: Docker Compose có tự động load .env không?**

A: Có, nhưng chúng ta đã thêm `env_file: - .env` để đảm bảo.

**Q: Tôi có thể dùng domain name thay vì IP không?**

A: Có! Đặt `HOST_IP=api.example.com` trong `.env`.

## Liên hệ

Nếu có vấn đề, vui lòng:
1. Kiểm tra file `.env` đã được tạo chưa
2. Kiểm tra `HOST_IP` có đúng không
3. Chạy `docker-compose logs` để xem lỗi
