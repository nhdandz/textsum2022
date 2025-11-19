# Hướng Dẫn Chuyển Mạng

## Tổng Quan

Khi chuyển project sang mạng khác, bạn chỉ cần:
1. Sửa file `.env`
2. Chạy script tự động `./change_network.sh <IP_MỚI>`

## Cách Sử Dụng Script Tự Động

```bash
# Ví dụ: Chuyển sang IP 192.168.1.100
./change_network.sh 192.168.1.100
```

Script sẽ tự động:
- ✅ Cập nhật tất cả IP trong `.env`
- ✅ Cấu hình Ollama listen trên 0.0.0.0 (nếu chưa có)
- ✅ Restart Ollama service
- ✅ Restart tất cả Docker containers
- ✅ (Tùy chọn) Xóa Kafka volume cũ nếu có lỗi

## Hoặc Thủ Công

### Bước 1: Sửa File .env

```bash
# Lấy IP hiện tại của máy
hostname -I | awk '{print $1}'

# Sửa HOST_IP trong .env
nano .env
# Thay đổi: HOST_IP=192.168.213.13 -> HOST_IP=<IP_MỚI>
```

### Bước 2: Cấu Hình Ollama (Chỉ Cần 1 Lần)

```bash
# Thêm OLLAMA_HOST vào systemd config
echo 'Environment="OLLAMA_HOST=0.0.0.0:11434"' | sudo tee -a /etc/systemd/system/ollama.service.d/override.conf

# Restart Ollama
sudo systemctl daemon-reload
sudo systemctl restart ollama

# Kiểm tra
ss -tlnp | grep 11434  # Phải thấy 0.0.0.0:11434, không phải 127.0.0.1
```

### Bước 3: Restart Docker Services

```bash
# Stop tất cả
docker compose down

# (Tùy chọn) Nếu có lỗi Kafka, xóa volume cũ:
docker volume rm textsum2022_kafka_data

# Start lại
docker compose up -d
```

### Bước 4: Kiểm Tra

```bash
# 1. Kiểm tra Ollama
curl http://<IP_MỚI>:11434/api/tags

# 2. Kiểm tra Kafka
docker logs kafka-1 --tail 30

# 3. Kiểm tra tất cả services
docker compose ps

# 4. Test message
python3 test_send_message.py
docker logs ollama-service --tail 20
```

## Các File Đã Được Sửa

Tất cả files sau đã được update để **tự động đọc từ .env**:

### ✅ Đã Fix - Không Cần Sửa Thủ Công
1. **docker-compose.yml** - dùng `${HOST_IP}`
2. **modules/root_kafka/multi_kafka.py** - dùng `os.getenv('STATUS_WEB_URL')`
3. **modules/root_kafka/send_data.py** - dùng `os.getenv('KAFKA_BOOTSTRAP_SERVERS')`
4. **modules/root_kafka/algo.json** - dùng `${HOST_IP}`, được expand tự động
5. **modules/algorithm_control/init.py** - expand `${HOST_IP}` trong algo.json
6. **modules/Single/Ollama/configs.json** - dùng env vars
7. **modules/Multi/Ollama/configs.json** - dùng env vars

### ⚠️ Lưu Ý: IPs Từ Máy Cũ
File `algo.json` vẫn còn một số IPs từ máy cũ `192.168.2.25`:
- Primera (algorId: 21, 28)
- HiMap (algorId: 17)
- MemSum (algorId: 16)
- BigBird (algorId: 7, 8)
- BertExt (algorId: 4)
- Match Sum (algorId: 5)

Nếu cần dùng các algo này, bạn phải:
1. Deploy các service này trên máy mới
2. Sửa IP trong `modules/root_kafka/algo.json`

## Kiểm Tra Nhanh

```bash
# Xem tất cả IPs trong project
grep -r "192.168" --include="*.json" --include="*.py" --include="*.yml" | grep -v ".pyc" | grep -v "test"
```

## Troubleshooting

### Kafka không khởi động
```bash
# Xóa volume và restart
docker compose down
docker volume rm textsum2022_kafka_data
docker compose up -d kafka-1
```

### Ollama connection refused từ container
```bash
# Kiểm tra Ollama listen ở đâu
ss -tlnp | grep 11434

# Phải thấy: 0.0.0.0:11434
# Nếu thấy: 127.0.0.1:11434 -> Ollama chưa config đúng

# Fix:
sudo nano /etc/systemd/system/ollama.service.d/override.conf
# Thêm: Environment="OLLAMA_HOST=0.0.0.0:11434"
sudo systemctl daemon-reload
sudo systemctl restart ollama
```

### Services không connect được
```bash
# Kiểm tra .env
cat .env | grep HOST_IP

# Kiểm tra IP máy
hostname -I

# Restart tất cả
docker compose restart
```
