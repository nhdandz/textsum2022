# Hướng Dẫn Upload Docker Images lên Docker Hub

## Tổng Quan

Hướng dẫn này sẽ giúp bạn:
1. Tạo tài khoản Docker Hub
2. Build và push images lên Docker Hub
3. Pull và deploy từ Docker Hub
4. Quản lý versions

## Yêu Cầu

- Tài khoản Docker Hub (free hoặc paid)
- Docker Engine đã cài đặt
- Đã build thành công các images locally

## Bước 1: Tạo Tài Khoản Docker Hub

### 1.1. Đăng ký tài khoản

1. Truy cập: https://hub.docker.com/signup
2. Đăng ký với email của bạn
3. Xác nhận email
4. Đăng nhập vào Docker Hub

### 1.2. Tạo Repository (Optional)

Bạn có thể tạo repository trước hoặc để script tự động tạo khi push:

1. Login vào Docker Hub: https://hub.docker.com
2. Click "Create Repository"
3. Chọn visibility:
   - **Public**: Miễn phí, mọi người đều xem được
   - **Private**: Cần paid plan, chỉ bạn truy cập được

## Bước 2: Login Docker Hub từ Terminal

```bash
# Login vào Docker Hub
docker login

# Nhập username và password khi được hỏi
# Username: your-dockerhub-username
# Password: your-password

# Hoặc dùng access token (khuyến nghị)
# Tạo token tại: https://hub.docker.com/settings/security
docker login -u your-username
```

## Bước 3: Cấu Hình Docker Hub Username

### Cách 1: Dùng file .env (Khuyến nghị)

```bash
# Copy file .env.example
cp .env.example .env

# Edit file .env
nano .env

# Điền thông tin:
DOCKER_USERNAME=your-dockerhub-username
VERSION=latest
```

### Cách 2: Set Environment Variable

```bash
# Linux/Mac
export DOCKER_USERNAME=your-dockerhub-username
export VERSION=v1.0.0

# Windows PowerShell
$env:DOCKER_USERNAME="your-dockerhub-username"
$env:VERSION="v1.0.0"

# Windows CMD
set DOCKER_USERNAME=your-dockerhub-username
set VERSION=v1.0.0
```

### Cách 3: Edit Script Trực Tiếp

Mở file `docker-build-and-push.sh` và sửa dòng:

```bash
DOCKER_USERNAME="${DOCKER_USERNAME:-your-dockerhub-username}"
```

Thành:

```bash
DOCKER_USERNAME="${DOCKER_USERNAME:-nhdandz}"  # Thay nhdandz bằng username của bạn
```

## Bước 4: Build và Push Images

### 4.1. Build và Push Tất Cả Services

```bash
# Make script executable
chmod +x docker-build-and-push.sh

# Run script
./docker-build-and-push.sh

# Hoặc với version cụ thể
VERSION=v1.0.0 ./docker-build-and-push.sh
```

Script sẽ:
1. ✅ Check login status
2. ✅ Build từng service image
3. ✅ Tag với version và latest
4. ✅ Push lên Docker Hub

### 4.2. Build và Push Từng Service Riêng Lẻ

```bash
# Set username
export DOCKER_USERNAME=your-username

# Build image
docker build -t $DOCKER_USERNAME/textsum2022-algo-control:latest \
  ./modules/algorithm_control

# Push image
docker push $DOCKER_USERNAME/textsum2022-algo-control:latest
```

### 4.3. Xem Build Progress

```bash
# Xem images đã build
docker images | grep textsum2022

# Kiểm tra image size
docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}" | grep textsum2022
```

## Bước 5: Verify Images trên Docker Hub

1. Truy cập: https://hub.docker.com/repositories/your-username
2. Kiểm tra các repositories đã được tạo:
   - `textsum2022-algo-control`
   - `textsum2022-root-kafka`
   - `textsum2022-single-kafka`
   - `textsum2022-single-texrank`
   - `textsum2022-multi-multexrank`
   - `textsum2022-text-similarity`

3. Click vào từng repository để xem:
   - Tags (latest, v1.0.0, etc.)
   - Image size
   - Last pushed time

## Bước 6: Pull Images từ Docker Hub

### 6.1. Pull Tất Cả Images

```bash
# Make script executable
chmod +x docker-pull.sh

# Run script
./docker-pull.sh

# Hoặc với version cụ thể
VERSION=v1.0.0 ./docker-pull.sh
```

### 6.2. Pull Từng Image Riêng

```bash
docker pull your-username/textsum2022-algo-control:latest
docker pull your-username/textsum2022-root-kafka:latest
# ... etc
```

### 6.3. Verify Downloaded Images

```bash
docker images | grep textsum2022
```

## Bước 7: Deploy từ Docker Hub

### 7.1. Update docker-compose.hub.yml

```bash
# Edit file
nano docker-compose.hub.yml

# Hoặc dùng .env
echo "DOCKER_USERNAME=your-username" > .env
echo "VERSION=latest" >> .env
```

### 7.2. Start Services

```bash
# Dùng docker-compose với file hub
docker-compose -f docker-compose.hub.yml up -d

# Hoặc tạo alias
alias docker-compose-hub='docker-compose -f docker-compose.hub.yml'
docker-compose-hub up -d
```

### 7.3. Verify Deployment

```bash
# Check containers
docker-compose -f docker-compose.hub.yml ps

# Check logs
docker-compose -f docker-compose.hub.yml logs -f

# Test APIs
curl http://localhost:6789/
curl http://localhost:9980/
curl http://localhost:9400/
```

## Quản Lý Versions

### Tagging Strategy

```bash
# Tag với semantic versioning
docker tag local-image:latest username/image:v1.0.0
docker tag local-image:latest username/image:v1.0
docker tag local-image:latest username/image:v1
docker tag local-image:latest username/image:latest

# Push all tags
docker push username/image:v1.0.0
docker push username/image:v1.0
docker push username/image:v1
docker push username/image:latest
```

### Update Version

```bash
# Build với version mới
VERSION=v1.1.0 ./docker-build-and-push.sh

# Deploy version mới
VERSION=v1.1.0 docker-compose -f docker-compose.hub.yml up -d

# Rollback về version cũ
VERSION=v1.0.0 docker-compose -f docker-compose.hub.yml up -d
```

## Best Practices

### 1. Image Tags

```bash
# ✅ GOOD: Semantic versioning
your-username/textsum2022-algo-control:v1.0.0
your-username/textsum2022-algo-control:v1.0
your-username/textsum2022-algo-control:latest

# ❌ BAD: Không có version
your-username/textsum2022-algo-control:latest  # only
```

### 2. Image Size Optimization

```dockerfile
# Dùng multi-stage builds
FROM python:3.9-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.9-slim
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY . .
CMD ["python", "app.py"]
```

### 3. Security

```bash
# Dùng Docker Content Trust
export DOCKER_CONTENT_TRUST=1

# Scan images for vulnerabilities
docker scout quickview your-username/textsum2022-algo-control:latest

# Hoặc dùng Trivy
trivy image your-username/textsum2022-algo-control:latest
```

### 4. Private Images

Nếu dùng private repositories:

```bash
# Pull từ private registry
docker login
docker pull your-username/private-image:latest

# Trong docker-compose.yml, không cần thay đổi gì
# Docker sẽ tự động dùng credentials đã login
```

## CI/CD Integration

### GitHub Actions Example

```yaml
# .github/workflows/docker-push.yml
name: Build and Push Docker Images

on:
  push:
    branches: [ main ]
    tags: [ 'v*' ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Login to Docker Hub
        uses: docker/login-action@v2
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}

      - name: Build and push
        run: |
          export DOCKER_USERNAME=${{ secrets.DOCKERHUB_USERNAME }}
          export VERSION=${GITHUB_REF#refs/tags/}
          ./docker-build-and-push.sh
```

### GitLab CI Example

```yaml
# .gitlab-ci.yml
docker-build:
  stage: build
  image: docker:latest
  services:
    - docker:dind
  script:
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD
    - export DOCKER_USERNAME=$CI_REGISTRY_USER
    - export VERSION=$CI_COMMIT_TAG
    - ./docker-build-and-push.sh
  only:
    - tags
```

## Alternatives to Docker Hub

### 1. GitHub Container Registry (ghcr.io)

```bash
# Login
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin

# Tag và push
docker tag local-image:latest ghcr.io/username/image:latest
docker push ghcr.io/username/image:latest

# Update docker-compose.hub.yml
image: ghcr.io/username/textsum2022-algo-control:latest
```

### 2. GitLab Container Registry

```bash
# Login
docker login registry.gitlab.com

# Tag và push
docker tag local-image:latest registry.gitlab.com/username/project/image:latest
docker push registry.gitlab.com/username/project/image:latest
```

### 3. Private Registry

```bash
# Run private registry
docker run -d -p 5000:5000 --name registry registry:2

# Tag và push
docker tag local-image:latest localhost:5000/image:latest
docker push localhost:5000/image:latest
```

## Troubleshooting

### Problem: Login Failed

```bash
# Solution 1: Use access token instead of password
# Tạo token tại: https://hub.docker.com/settings/security
docker login -u username

# Solution 2: Logout and login again
docker logout
docker login
```

### Problem: Push Denied

```bash
# Check if you're logged in
docker info | grep Username

# Check repository exists and you have write access
# Private repos require paid plan
```

### Problem: Image Too Large

```bash
# Check image size
docker images | grep textsum2022

# Optimize Dockerfile:
# - Use slim base images
# - Remove build dependencies
# - Use .dockerignore
# - Multi-stage builds
```

### Problem: Slow Push

```bash
# Check your internet connection
# Large images take time

# Use docker layer caching
# Only changed layers will be pushed

# Compress before pushing
docker save image:tag | gzip > image.tar.gz
```

## Image Pricing

### Docker Hub Free Tier
- ✅ Unlimited public repositories
- ✅ Unlimited pulls
- ✅ 1 private repository
- ❌ Limited to 200 pulls per 6 hours (unauthenticated)

### Docker Hub Pro ($5/month)
- ✅ Unlimited private repositories
- ✅ Unlimited pulls
- ✅ Parallel builds
- ✅ Priority support

### Docker Hub Teams ($7/user/month)
- ✅ All Pro features
- ✅ Team collaboration
- ✅ Advanced permissions

## Monitoring và Management

### View Image Statistics

```bash
# Xem pulls count trên Docker Hub website
# https://hub.docker.com/r/username/image/analytics

# Check image layers
docker history username/image:latest

# Inspect image
docker inspect username/image:latest

# Check vulnerabilities
docker scout cves username/image:latest
```

### Cleanup Old Images

```bash
# Xóa images cũ locally
docker image prune -a

# Delete tags trên Docker Hub
# Phải làm thủ công qua web interface:
# https://hub.docker.com/r/username/image/tags
```

## Summary Commands

```bash
# === Build và Push ===
./docker-build-and-push.sh                    # Build và push tất cả
VERSION=v1.0.0 ./docker-build-and-push.sh     # Với version cụ thể

# === Pull ===
./docker-pull.sh                              # Pull tất cả
docker pull username/textsum2022-algo-control # Pull một image

# === Deploy ===
docker-compose -f docker-compose.hub.yml up -d   # Deploy từ Hub
docker-compose -f docker-compose.hub.yml down    # Stop

# === Management ===
docker images | grep textsum2022              # List images
docker rmi username/textsum2022-algo-control  # Remove image
docker login                                  # Login to Hub
docker logout                                 # Logout
```

## Support

Nếu gặp vấn đề:
1. Check Docker Hub status: https://status.docker.com/
2. Docker Hub documentation: https://docs.docker.com/docker-hub/
3. Docker forums: https://forums.docker.com/

---

**Chúc bạn deploy thành công!** 🚀
