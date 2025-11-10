# Hướng Dẫn Deployment Docker cho Text Summarization System

## Tổng Quan

Hệ thống Text Summarization 2022 đã được dockerize hoàn toàn với 12 microservices và Kafka infrastructure.

### Kiến Trúc Hệ Thống

```
┌─────────────────────────────────────────────────────────────┐
│                    Infrastructure Layer                      │
├─────────────────────────────────────────────────────────────┤
│  Zookeeper  │  Kafka  │  Schema Registry  │  Redpanda UI   │
│   :2181     │  :9092  │      :8881        │     :8088      │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                      Core Services                           │
├─────────────────────────────────────────────────────────────┤
│  algo-control (:6789)  │  app-process (:9980)               │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    Kafka Router Layer                        │
├─────────────────────────────────────────────────────────────┤
│  root-kafka  │  single-kafka  │  multi-kafka                │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────┬──────────────────────────────┐
│   Single Document Services   │   Multi Document Services    │
├──────────────────────────────┼──────────────────────────────┤
│  • textrank                  │  • m-textrank                │
│  • lexrank                   │  • m-lexrank                 │
│  • lsa                       │  • m-lsa                     │
└──────────────────────────────┴──────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│              Additional Services                             │
├─────────────────────────────────────────────────────────────┤
│  clustering (:9400) - Text Similarity Service                │
└─────────────────────────────────────────────────────────────┘
```

## Các Services và Ports

### Infrastructure Services
- **Zookeeper**: Port 2181 - Kafka coordination
- **Kafka**: Port 9092 - Message broker
- **Schema Registry**: Port 8881 - Schema management
- **Redpanda Console**: Port 8088 - Kafka monitoring UI

### Application Services
- **algo-control**: Port 6789 - Algorithm control API
- **app-process**: Port 9980 - Document processing API
- **clustering**: Port 9400 - Text similarity API
- **root-kafka**: Kafka consumer/producer - Main router
- **single-kafka**: Kafka consumer/producer - Single doc router
- **multi-kafka**: Kafka consumer/producer - Multi doc router
- **textrank, lexrank, lsa**: Kafka consumers - Single doc algorithms
- **m-textrank, m-lexrank, m-lsa**: Kafka consumers - Multi doc algorithms

## Yêu Cầu Hệ Thống

- Docker Engine 20.10+
- Docker Compose 2.0+
- RAM: Tối thiểu 8GB (khuyến nghị 16GB)
- Disk: Tối thiểu 20GB trống
- CPU: 4 cores trở lên

## Cài Đặt và Chạy

### 1. Build và Start Tất Cả Services

```bash
# Di chuyển vào thư mục project
cd /path/to/textsum2022

# Build tất cả images
docker-compose build

# Start tất cả services
docker-compose up -d

# Xem logs
docker-compose logs -f

# Xem logs của một service cụ thể
docker-compose logs -f app-process
```

### 2. Start Từng Nhóm Services (Khuyến Nghị)

**Bước 1: Start Infrastructure**
```bash
docker-compose up -d zookeeper kafka schema-registry redpanda-console
```

**Bước 2: Kiểm tra Kafka đã ready**
```bash
# Đợi ~30 giây để Kafka hoàn toàn khởi động
docker-compose logs kafka | grep "started"
```

**Bước 3: Start Core Services**
```bash
docker-compose up -d algo-control app-process
```

**Bước 4: Start Kafka Routers**
```bash
docker-compose up -d root-kafka single-kafka multi-kafka
```

**Bước 5: Start Algorithm Services**
```bash
# Single document services
docker-compose up -d textrank lexrank lsa

# Multi document services
docker-compose up -d m-textrank m-lexrank m-lsa

# Additional services
docker-compose up -d clustering
```

### 3. Verify Services

```bash
# Kiểm tra tất cả containers đang chạy
docker-compose ps

# Kiểm tra health của services
docker-compose ps | grep "Up"

# Test API endpoints
curl http://localhost:6789/     # algo-control
curl http://localhost:9980/     # app-process
curl http://localhost:9400/     # clustering

# Truy cập Kafka UI
# Mở browser: http://localhost:8088
```

## Quản Lý Services

### Stop Services

```bash
# Stop tất cả
docker-compose down

# Stop nhưng giữ lại volumes
docker-compose stop

# Stop một service cụ thể
docker-compose stop textrank
```

### Restart Services

```bash
# Restart tất cả
docker-compose restart

# Restart một service
docker-compose restart app-process
```

### Xem Logs

```bash
# Logs tất cả services
docker-compose logs -f

# Logs một service với tail 100 dòng cuối
docker-compose logs -f --tail=100 textrank

# Logs nhiều services
docker-compose logs -f textrank lexrank lsa
```

### Scale Services (nếu cần)

```bash
# Scale textrank service lên 3 instances
docker-compose up -d --scale textrank=3

# Lưu ý: Phải cấu hình Kafka consumer group đúng
```

## Monitoring và Debugging

### 1. Kafka Monitoring với Redpanda Console

Truy cập: http://localhost:8088

- Xem topics
- Xem messages trong topics
- Monitor consumer groups
- Xem lag của consumers

### 2. Debug Container

```bash
# Exec vào container
docker-compose exec app-process bash

# Hoặc nếu không có bash
docker-compose exec app-process sh

# Xem logs realtime
docker-compose logs -f app-process

# Inspect container
docker inspect textsum2022-app-process-1
```

### 3. Check Resource Usage

```bash
# Xem resource usage của tất cả containers
docker stats

# Xem của một container cụ thể
docker stats textsum2022-textrank-1
```

## Troubleshooting

### Problem: Container không start

```bash
# Xem logs chi tiết
docker-compose logs [service-name]

# Rebuild image
docker-compose build --no-cache [service-name]

# Restart service
docker-compose restart [service-name]
```

### Problem: Kafka connection errors

```bash
# Kiểm tra Kafka đang chạy
docker-compose ps kafka

# Kiểm tra Kafka logs
docker-compose logs kafka

# Test Kafka từ bên trong network
docker-compose exec app-process ping kafka
```

### Problem: Out of memory

```bash
# Tăng memory limit trong docker-compose.yml
# Thêm vào service cần thiết:
deploy:
  resources:
    limits:
      memory: 2G
```

### Problem: Port đã được sử dụng

```bash
# Kiểm tra port đang được dùng bởi process nào
sudo lsof -i :9092

# Thay đổi port mapping trong docker-compose.yml
# Ví dụ: "9093:9092" thay vì "9092:9092"
```

## Cấu Hình Nâng Cao

### 1. Thay đổi Kafka Bootstrap Server

Trong `docker-compose.yml`, tất cả services đã được cấu hình với biến môi trường:
```yaml
environment:
  - KAFKA_BOOTSTRAP_SERVERS=kafka:9092
```

Nếu cần connect từ bên ngoài Docker network, sửa `KAFKA_ADVERTISED_LISTENERS`:
```yaml
KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://localhost:9092
```

### 2. Persistent Data

Volumes đã được định nghĩa cho Kafka và Zookeeper:
```yaml
volumes:
  kafka_data:
  zookeeper_data:
```

Để xóa data hoàn toàn:
```bash
docker-compose down -v
```

### 3. Production Deployment

Để deploy production, cần:

1. **Tăng resources cho Kafka:**
```yaml
KAFKA_HEAP_OPTS: "-Xms2G -Xmx4G"
```

2. **Enable authentication & encryption**

3. **Setup monitoring với Prometheus + Grafana**

4. **Configure backup cho volumes**

5. **Setup load balancer cho các API services**

## API Usage Examples

### 1. Document Processing API (port 9980)

```bash
# Get service status
curl http://localhost:9980/

# Get number of pages
curl -X POST http://localhost:9980/get_number_page \
  -H "Content-Type: application/json" \
  -d '{
    "encode": "base64_encoded_document",
    "file_type": "pdf"
  }'

# Get content
curl -X POST http://localhost:9980/get_content \
  -H "Content-Type: application/json" \
  -d '{
    "documents": [
      {
        "encode": "base64_encoded_document",
        "file_type": "pdf",
        "page_from": 1,
        "page_to": 10,
        "documents_id": "doc123"
      }
    ]
  }'
```

### 2. Algorithm Control API (port 6789)

```bash
# Get service status
curl http://localhost:6789/

# Control algorithm status
curl -X POST http://localhost:6789/control \
  -H "Content-Type: application/json" \
  -d '{
    "algorithm_id": "textrank",
    "action": "start"
  }'
```

### 3. Clustering API (port 9400)

```bash
# Get service status
curl http://localhost:9400/

# Text clustering
curl -X POST http://localhost:9400/TextClustering \
  -H "Content-Type: application/json" \
  -d '{
    "list_doc": ["document1", "document2", "document3"]
  }'
```

## Backup và Restore

### Backup

```bash
# Backup volumes
docker run --rm -v textsum2022_kafka_data:/data -v $(pwd):/backup \
  alpine tar czf /backup/kafka_data_backup.tar.gz -C /data .

# Backup images
docker save -o textsum_images.tar \
  textsum2022-app-process \
  textsum2022-textrank \
  textsum2022-algo-control
```

### Restore

```bash
# Restore volumes
docker run --rm -v textsum2022_kafka_data:/data -v $(pwd):/backup \
  alpine sh -c "cd /data && tar xzf /backup/kafka_data_backup.tar.gz"

# Restore images
docker load -i textsum_images.tar
```

## Maintenance

### Update Code

```bash
# Pull latest code
git pull

# Rebuild specific service
docker-compose build app-process

# Restart service với zero-downtime (nếu có nhiều instances)
docker-compose up -d --no-deps app-process
```

### Clean Up

```bash
# Remove stopped containers
docker-compose rm

# Remove unused images
docker image prune -a

# Remove unused volumes (CẨN THẬN: Mất data!)
docker volume prune

# Complete cleanup (CẨN THẬN!)
docker-compose down -v --rmi all
```

## Performance Tuning

### 1. Kafka Performance

```yaml
# Trong docker-compose.yml
environment:
  # Tăng batch size
  KAFKA_REPLICA_FETCH_MAX_BYTES: 10485760
  # Tăng buffer memory
  KAFKA_SOCKET_REQUEST_MAX_BYTES: 104857600
```

### 2. Python Services

```dockerfile
# Trong Dockerfile, thêm:
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
```

### 3. Resource Limits

```yaml
# Thêm vào mỗi service trong docker-compose.yml
deploy:
  resources:
    limits:
      cpus: '2.0'
      memory: 2G
    reservations:
      cpus: '1.0'
      memory: 1G
```

## Support

Nếu gặp vấn đề, kiểm tra:
1. Logs của service: `docker-compose logs [service-name]`
2. Kafka topics và messages: http://localhost:8088
3. Container status: `docker-compose ps`
4. Resource usage: `docker stats`

---

**Lưu ý:** File này được tạo tự động khi dockerize project. Cập nhật theo nhu cầu thực tế của bạn.
