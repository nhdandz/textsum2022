# Text Summarization System - Docker Quick Start

## Tổng Quan

Hệ thống tóm tắt văn bản tiếng Việt với 12 microservices được đóng gói hoàn toàn trong Docker.

## Yêu Cầu

- Docker Engine 20.10+
- Docker Compose 2.0+
- RAM: 8GB+ (khuyến nghị 16GB)
- Disk: 20GB trống

## Quick Start

### 1. Start Tất Cả Services

```bash
# Cách 1: Sử dụng script helper (khuyến nghị)
./docker-start.sh

# Cách 2: Sử dụng docker-compose trực tiếp
docker-compose up -d
```

### 2. Kiểm Tra Status

```bash
# Sử dụng script helper
./docker-status.sh

# Hoặc kiểm tra thủ công
docker-compose ps
```

### 3. Xem Logs

```bash
# Xem logs của một service
./docker-logs.sh textrank

# Xem logs tất cả
docker-compose logs -f
```

### 4. Stop Services

```bash
# Sử dụng script
./docker-stop.sh

# Hoặc docker-compose
docker-compose down
```

## Các Services và Ports

| Service | Port | Mô Tả |
|---------|------|-------|
| **API Services** | | |
| algo-control | 6789 | Quản lý trạng thái thuật toán |
| app-process | 9980 | Xử lý và trích xuất nội dung tài liệu |
| clustering | 9400 | Phân cụm văn bản (text similarity) |
| **Infrastructure** | | |
| kafka | 9092 | Message broker |
| zookeeper | 2181 | Kafka coordination |
| schema-registry | 8881 | Schema management |
| redpanda-console | 8088 | Kafka monitoring UI |
| **Kafka Consumers** | | |
| root-kafka | - | Router chính |
| single-kafka | - | Router tài liệu đơn |
| multi-kafka | - | Router đa tài liệu |
| textrank | - | Thuật toán TextRank (đơn) |
| lexrank | - | Thuật toán LexRank (đơn) |
| lsa | - | Thuật toán LSA (đơn) |
| m-textrank | - | Thuật toán TextRank (đa) |
| m-lexrank | - | Thuật toán LexRank (đa) |
| m-lsa | - | Thuật toán LSA (đa) |

## Test APIs

### 1. Health Checks

```bash
curl http://localhost:6789/     # algo-control
curl http://localhost:9980/     # app-process
curl http://localhost:9400/     # clustering
```

### 2. Kafka UI

Mở browser: **http://localhost:8088**

Ở đây bạn có thể:
- Xem các Kafka topics
- Monitor messages
- Kiểm tra consumer groups
- Xem consumer lag

### 3. Process Document

```bash
curl -X POST http://localhost:9980/get_content \
  -H "Content-Type: application/json" \
  -d '{
    "documents": [{
      "encode": "base64_encoded_document",
      "file_type": "pdf",
      "page_from": 1,
      "page_to": 10,
      "documents_id": "doc123"
    }]
  }'
```

## Cấu Trúc Project

```
textsum2022/
├── docker-compose.yml              # Cấu hình tất cả services
├── docker-compose-kafka.yaml       # Chỉ Kafka infrastructure
├── .dockerignore                   # Ignore files cho Docker build
├── DOCKER_DEPLOYMENT.md            # Hướng dẫn chi tiết
├── README_DOCKER.md                # File này
├── docker-start.sh                 # Script start services
├── docker-stop.sh                  # Script stop services
├── docker-logs.sh                  # Script xem logs
├── docker-status.sh                # Script kiểm tra status
└── modules/
    ├── algorithm_control/
    │   ├── Dockerfile
    │   └── requirements.txt
    ├── root_kafka/
    │   ├── Dockerfile
    │   └── requirements.txt
    ├── single_kafka/
    │   ├── Dockerfile
    │   └── requirements.txt
    ├── Single/
    │   └── TexRank/
    │       ├── Dockerfile
    │       └── requirements.txt
    ├── Multi/
    │   └── MulTexRank/
    │       ├── Dockerfile
    │       └── requirements.txt
    └── Text-similarity/
        ├── Dockerfile
        └── requirements.txt
```

## Các Scripts Helper

### docker-start.sh
Start tất cả services theo thứ tự đúng:
1. Infrastructure (Zookeeper, Kafka)
2. Core services (algo-control, app-process)
3. Kafka routers
4. Algorithm services

### docker-stop.sh
Stop tất cả services một cách an toàn

### docker-status.sh
Hiển thị:
- Container status
- Resource usage (CPU, Memory)
- API health checks

### docker-logs.sh
Xem logs của một service cụ thể

## Troubleshooting

### Services không start
```bash
# Xem logs để debug
docker-compose logs [service-name]

# Rebuild image
docker-compose build --no-cache [service-name]

# Restart
docker-compose restart [service-name]
```

### Kafka connection errors
```bash
# Kiểm tra Kafka logs
docker-compose logs kafka

# Đảm bảo Kafka đã start hoàn toàn (đợi ~60s)
docker-compose ps kafka
```

### Port conflict
```bash
# Kiểm tra port đang được dùng
sudo lsof -i :9092

# Hoặc thay đổi port trong docker-compose.yml
```

### Out of memory
```bash
# Stop một số services không cần thiết
docker-compose stop m-textrank m-lexrank m-lsa

# Hoặc tăng Docker memory limit
# Docker Desktop > Settings > Resources > Memory
```

## Maintenance

### Update code
```bash
git pull
docker-compose build
docker-compose up -d
```

### Cleanup
```bash
# Remove stopped containers
docker-compose rm

# Remove unused images
docker image prune -a

# CẢNH BÁO: Remove volumes (mất data!)
docker-compose down -v
```

### Backup
```bash
# Backup volumes
docker run --rm \
  -v textsum2022_kafka_data:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/kafka_backup.tar.gz -C /data .
```

## Development

### Build một service cụ thể
```bash
docker-compose build textrank
```

### Run service trong interactive mode
```bash
docker-compose run --rm textrank bash
```

### Override command
```bash
docker-compose run --rm textrank python -c "import nltk; print(nltk.__version__)"
```

## Production Considerations

Khi deploy production, cần:

1. **Tăng resources**: Sửa `KAFKA_HEAP_OPTS` trong docker-compose.yml
2. **Enable monitoring**: Thêm Prometheus + Grafana
3. **Setup backup**: Automated backup cho Kafka volumes
4. **Load balancing**: Nginx/HAProxy cho các API services
5. **Security**: Enable Kafka authentication & SSL
6. **High availability**: Kafka cluster với nhiều brokers

## Tài Liệu Chi Tiết

Xem file `DOCKER_DEPLOYMENT.md` để biết:
- Kiến trúc hệ thống chi tiết
- API usage examples
- Performance tuning
- Advanced configuration
- Backup & restore procedures

## Support

Nếu gặp vấn đề:
1. Kiểm tra logs: `./docker-logs.sh [service-name]`
2. Kiểm tra status: `./docker-status.sh`
3. Xem Kafka UI: http://localhost:8088
4. Đọc tài liệu chi tiết: `DOCKER_DEPLOYMENT.md`

---

**Chúc bạn sử dụng hệ thống hiệu quả!** 🚀
