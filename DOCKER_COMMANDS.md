# Docker Commands Quick Reference

## 🚀 Quick Start

### First Time Setup
```bash
# 1. Setup Docker Hub username
./docker-setup-username.sh

# 2. Login to Docker Hub
docker login

# 3a. Build và push lên Docker Hub
./docker-build-and-push.sh

# 3b. Hoặc chạy local
./docker-start.sh
```

## 📦 Build & Push to Docker Hub

### Build và Push Tất Cả
```bash
# Build và push với tag latest
./docker-build-and-push.sh

# Build và push với version cụ thể
VERSION=v1.0.0 ./docker-build-and-push.sh

# Build và push với custom username
DOCKER_USERNAME=myusername ./docker-build-and-push.sh
```

### Build Thủ Công
```bash
# Build một service
docker build -t myusername/textsum2022-algo-control:latest ./modules/algorithm_control

# Push lên Docker Hub
docker push myusername/textsum2022-algo-control:latest

# Tag với nhiều versions
docker tag myusername/textsum2022-algo-control:latest myusername/textsum2022-algo-control:v1.0.0
docker push myusername/textsum2022-algo-control:v1.0.0
```

## ⬇️ Pull from Docker Hub

### Pull Tất Cả Images
```bash
# Pull với script
./docker-pull.sh

# Pull với version cụ thể
VERSION=v1.0.0 ./docker-pull.sh
```

### Pull Thủ Công
```bash
# Pull một image
docker pull myusername/textsum2022-algo-control:latest

# Pull tất cả bằng docker-compose
docker-compose -f docker-compose.hub.yml pull
```

## 🎯 Deployment

### Local Deployment (Build từ source)
```bash
# Start all services
./docker-start.sh

# Hoặc dùng docker-compose
docker-compose up -d

# View logs
./docker-logs.sh [service-name]

# Check status
./docker-status.sh

# Stop all
./docker-stop.sh
```

### Docker Hub Deployment (Pull từ registry)
```bash
# Start from Docker Hub images
docker-compose -f docker-compose.hub.yml up -d

# Update services (pull new version)
docker-compose -f docker-compose.hub.yml pull
docker-compose -f docker-compose.hub.yml up -d

# Stop
docker-compose -f docker-compose.hub.yml down
```

## 🔧 Management Commands

### Container Management
```bash
# Xem tất cả containers
docker-compose ps

# Restart một service
docker-compose restart textrank

# Stop một service
docker-compose stop textrank

# Remove containers
docker-compose down

# Remove containers + volumes (CẨN THẬN: mất data!)
docker-compose down -v
```

### Logs & Debugging
```bash
# View logs tất cả services
docker-compose logs -f

# View logs một service
docker-compose logs -f textrank

# View logs 100 dòng cuối
docker-compose logs -f --tail=100 textrank

# Exec vào container
docker-compose exec textrank bash

# Check resource usage
docker stats
```

### Image Management
```bash
# List tất cả images
docker images

# List images của project
docker images | grep textsum2022

# Remove một image
docker rmi myusername/textsum2022-algo-control:latest

# Remove tất cả unused images
docker image prune -a

# Check image size
docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"
```

### Network & Volume
```bash
# List networks
docker network ls

# Inspect network
docker network inspect textsum-network

# List volumes
docker volume ls

# Remove unused volumes (CẨN THẬN!)
docker volume prune
```

## 🔍 Monitoring & Health Checks

### Service Health
```bash
# API health checks
curl http://localhost:6789/      # algo-control
curl http://localhost:9980/      # app-process
curl http://localhost:9400/      # clustering

# Open Kafka UI
open http://localhost:8088       # Mac
xdg-open http://localhost:8088   # Linux
start http://localhost:8088      # Windows
```

### Resource Monitoring
```bash
# Container stats
docker stats

# Specific container
docker stats textsum2022-textrank-1

# System-wide
docker system df

# Detailed info
docker system info
```

## 🔄 Version Management

### Tagging
```bash
# Tag local image
docker tag local-image:latest username/image:v1.0.0

# Push với version
docker push username/image:v1.0.0

# Deploy version cụ thể
VERSION=v1.0.0 docker-compose -f docker-compose.hub.yml up -d
```

### Rollback
```bash
# Deploy version cũ
VERSION=v0.9.0 docker-compose -f docker-compose.hub.yml pull
VERSION=v0.9.0 docker-compose -f docker-compose.hub.yml up -d
```

## 🧹 Cleanup

### Basic Cleanup
```bash
# Stop và remove containers
docker-compose down

# Remove stopped containers
docker-compose rm

# Remove unused images
docker image prune

# Remove unused volumes
docker volume prune

# Remove unused networks
docker network prune
```

### Deep Cleanup (CẨN THẬN!)
```bash
# Remove everything không được dùng
docker system prune -a

# Remove everything bao gồm volumes
docker system prune -a --volumes

# Force remove tất cả containers
docker rm -f $(docker ps -aq)

# Force remove tất cả images
docker rmi -f $(docker images -q)
```

## 🔐 Docker Hub Authentication

### Login & Logout
```bash
# Login với username/password
docker login

# Login với token (khuyến nghị)
docker login -u username

# Login vào custom registry
docker login registry.example.com

# Logout
docker logout

# Check login status
docker info | grep Username
```

### Access Tokens
```bash
# Tạo token tại: https://hub.docker.com/settings/security

# Login với token
echo "YOUR_TOKEN" | docker login -u USERNAME --password-stdin

# Store in environment
export DOCKER_TOKEN="your-token"
echo $DOCKER_TOKEN | docker login -u USERNAME --password-stdin
```

## 📊 Troubleshooting

### Check Logs
```bash
# Service không start
docker-compose logs [service-name]

# Kafka errors
docker-compose logs kafka | grep ERROR

# Python errors
docker-compose logs textrank | grep -i error
```

### Rebuild Services
```bash
# Rebuild tất cả
docker-compose build --no-cache

# Rebuild một service
docker-compose build --no-cache textrank

# Force recreate containers
docker-compose up -d --force-recreate
```

### Network Issues
```bash
# Check network connectivity
docker-compose exec textrank ping kafka

# Check DNS resolution
docker-compose exec textrank nslookup kafka

# Recreate network
docker-compose down
docker network rm textsum-network
docker-compose up -d
```

### Port Conflicts
```bash
# Check port usage
sudo lsof -i :9092
sudo netstat -tulpn | grep 9092

# Kill process on port
sudo kill -9 $(sudo lsof -t -i:9092)
```

## 🎨 Advanced Usage

### Scale Services
```bash
# Scale horizontally
docker-compose up -d --scale textrank=3

# Note: Phải config Kafka consumer groups đúng
```

### Override Configuration
```bash
# Override command
docker-compose run --rm textrank python -c "print('test')"

# Override environment
docker-compose run -e KAFKA_BOOTSTRAP_SERVERS=custom:9092 textrank

# Use custom compose file
docker-compose -f docker-compose.yml -f docker-compose.override.yml up -d
```

### Backup & Restore
```bash
# Backup volumes
docker run --rm -v textsum2022_kafka_data:/data -v $(pwd):/backup \
  alpine tar czf /backup/kafka_backup.tar.gz -C /data .

# Restore volumes
docker run --rm -v textsum2022_kafka_data:/data -v $(pwd):/backup \
  alpine sh -c "cd /data && tar xzf /backup/kafka_backup.tar.gz"

# Export images
docker save myusername/textsum2022-algo-control:latest | gzip > algo-control.tar.gz

# Import images
docker load < algo-control.tar.gz
```

## 📝 Environment Variables

### Set via .env file
```bash
# Create .env
cat > .env << EOF
DOCKER_USERNAME=myusername
VERSION=v1.0.0
KAFKA_BOOTSTRAP_SERVERS=kafka:9092
EOF

# Docker Compose tự động load .env
docker-compose up -d
```

### Set via command line
```bash
# Linux/Mac
export DOCKER_USERNAME=myusername
docker-compose up -d

# Windows PowerShell
$env:DOCKER_USERNAME="myusername"
docker-compose up -d
```

## 🔗 Quick Links

| Resource | URL |
|----------|-----|
| Docker Hub | https://hub.docker.com |
| Docker Docs | https://docs.docker.com |
| Docker Compose Docs | https://docs.docker.com/compose |
| Kafka UI (local) | http://localhost:8088 |
| API Documentation | See DOCKER_DEPLOYMENT.md |

## 📞 Need Help?

```bash
# Docker help
docker --help
docker-compose --help

# Service-specific help
docker-compose logs [service-name]

# Check status
./docker-status.sh

# Read documentation
cat DOCKER_HUB_GUIDE.md
cat DOCKER_DEPLOYMENT.md
cat README_DOCKER.md
```

---

**Pro Tip**: Add aliases to your `~/.bashrc` or `~/.zshrc`:

```bash
# Add these to your shell config
alias dc='docker-compose'
alias dcl='docker-compose logs -f'
alias dcp='docker-compose ps'
alias dce='docker-compose exec'
alias dch='docker-compose -f docker-compose.hub.yml'
```

Then reload: `source ~/.bashrc`

Now you can use:
- `dc up -d` instead of `docker-compose up -d`
- `dcl textrank` instead of `docker-compose logs -f textrank`
- `dcp` instead of `docker-compose ps`
- `dch up -d` for Docker Hub deployment
