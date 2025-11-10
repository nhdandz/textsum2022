# Quick Start - Cấu hình IP từ .env

## TL;DR

```bash
# 1. Thiết lập HOST_IP trong .env (đã có sẵn, chỉ cần sửa nếu muốn)
nano .env  # Thay đổi HOST_IP nếu cần

# 2. Thay thế tất cả IP tĩnh trong code (chỉ chạy 1 lần)
python3 replace_ips_simple.py

# 3. Cài python-dotenv (nếu chưa có)
pip install python-dotenv

# 4. Chuẩn bị build (copy .env vào modules)
./prepare_build.sh

# 5. Build và chạy Docker Compose
docker-compose build
docker-compose up -d
```

## Chi tiết

### Bước 1: Cấu hình IP

File `.env` đã được tạo sẵn với cấu hình mặc định. Chỉnh sửa nếu cần:

```bash
# Mở file .env
nano .env

# Thay đổi HOST_IP nếu cần
HOST_IP=192.168.210.42  # Thay bằng IP máy của bạn
```

### Bước 2: Cài dependencies

```bash
pip install python-dotenv
```

### Bước 3: Thay thế IP tĩnh (chỉ chạy 1 lần)

**⚠️ CHÚ Ý**: Chỉ cần chạy lệnh này **1 lần duy nhất** khi lần đầu thiết lập!

```bash
python3 replace_ips_simple.py
```

Script này sẽ thay thế tất cả các IP `192.168.210.42` và `192.168.2.25` thành `${HOST_IP}` trong:
- File Python (`.py`)
- File JSON (`.json`)
- File cấu hình (`.yaml`, `.yml`)

### Bước 4: Chuẩn bị build Docker

```bash
./prepare_build.sh
```

Script này sẽ copy file `.env` vào các module directories.

### Bước 5: Sử dụng trong code

#### Python files

```python
# Thêm vào đầu file Python
import os
from dotenv import load_dotenv

load_dotenv()

# Sử dụng
host_ip = os.getenv('HOST_IP', '192.168.210.42')
kafka_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', f'{host_ip}:9092')
```

Hoặc dùng helper:

```python
from env_config import HOST_IP, KAFKA_BOOTSTRAP_SERVERS

bootstrap_servers = [KAFKA_BOOTSTRAP_SERVERS]
```

#### JSON files

```python
from json_env_loader import load_json_with_env

# Thay vì json.load()
config = load_json_with_env('configs.json')
```

### Bước 6: Build và chạy Docker

```bash
# Build tất cả images
docker-compose build

# Chạy tất cả services
docker-compose up -d

# Xem logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Files đã tạo

| File | Mục đích |
|------|----------|
| `.env` | Chứa cấu hình HOST_IP |
| `env_config.py` | Helper load env cho Python |
| `json_env_loader.py` | Helper load JSON với env vars |
| `replace_ips_simple.py` | Script thay thế IP tĩnh |
| `prepare_build.sh` | Script chuẩn bị build Docker |
| `ENV_SETUP_GUIDE.md` | Hướng dẫn chi tiết |
| `requirements-env.txt` | Python dependencies cho env |

## Thay đổi IP sau này

Nếu muốn đổi IP:

```bash
# Chỉ cần sửa file .env
echo "HOST_IP=192.168.1.100" > .env

# Restart Docker
docker-compose restart
```

## Lỗi thường gặp khi build

### ❌ Lỗi "isqrt==0.9.9 not found"
✅ **Đã được sửa!** File `modules/Text-similarity/requirements.txt` đã cập nhật thành `isqrt==1.1.0`

### ❌ Lỗi "numpy.dtype size changed"
✅ **Đã được sửa!** Numpy được cài trước scikit-learn trong Dockerfile:
```dockerfile
RUN pip install --no-cache-dir numpy==1.23.5 && \
    pip install --no-cache-dir -r requirements.txt
```

### ❌ Service không kết nối được
Kiểm tra `HOST_IP` trong `.env` có đúng không:
```bash
cat .env | grep HOST_IP
# Nếu sai, sửa lại
nano .env
```

### ❌ python-dotenv not found
Cài thêm dependency:
```bash
pip install python-dotenv
```

## Xem hướng dẫn đầy đủ

Xem file `ENV_SETUP_GUIDE.md` để biết thêm chi tiết.
