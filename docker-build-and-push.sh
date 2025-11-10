#!/bin/bash

# Docker Hub Configuration
# Thay đổi DOCKER_USERNAME thành username Docker Hub của bạn
DOCKER_USERNAME="${DOCKER_USERNAME:-your-dockerhub-username}"
PROJECT_NAME="textsum2022"
VERSION="${VERSION:-latest}"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "========================================="
echo "Docker Build and Push to Docker Hub"
echo "========================================="
echo ""

# Check if logged in to Docker Hub
echo -e "${BLUE}Checking Docker Hub login...${NC}"
if ! docker info | grep -q "Username: $DOCKER_USERNAME"; then
    echo -e "${YELLOW}Not logged in to Docker Hub. Please login:${NC}"
    docker login
    if [ $? -ne 0 ]; then
        echo -e "${RED}Failed to login to Docker Hub. Exiting.${NC}"
        exit 1
    fi
fi

echo -e "${GREEN}✓ Logged in to Docker Hub${NC}"
echo ""

# Define services and their build contexts
declare -A SERVICES=(
    ["algo-control"]="./modules/algorithm_control"
    ["root-kafka"]="./modules/root_kafka"
    ["single-kafka"]="./modules/single_kafka"
    ["single-texrank"]="./modules/Single/TexRank"
    ["multi-multexrank"]="./modules/Multi/MulTexRank"
    ["text-similarity"]="./modules/Text-similarity"
)

# Function to build and push an image
build_and_push() {
    local service_name=$1
    local build_context=$2
    local image_name="$DOCKER_USERNAME/$PROJECT_NAME-$service_name"

    echo -e "${BLUE}Building $service_name...${NC}"

    # Build image
    docker build -t "$image_name:$VERSION" -t "$image_name:latest" "$build_context"

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Build successful: $image_name${NC}"

        # Push both tags
        echo -e "${BLUE}Pushing $image_name:$VERSION...${NC}"
        docker push "$image_name:$VERSION"

        if [ "$VERSION" != "latest" ]; then
            echo -e "${BLUE}Pushing $image_name:latest...${NC}"
            docker push "$image_name:latest"
        fi

        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓ Push successful: $image_name${NC}"
        else
            echo -e "${RED}✗ Failed to push: $image_name${NC}"
            return 1
        fi
    else
        echo -e "${RED}✗ Build failed: $service_name${NC}"
        return 1
    fi

    echo ""
}

# Build and push all services
echo -e "${BLUE}Building and pushing all services...${NC}"
echo ""

for service in "${!SERVICES[@]}"; do
    build_and_push "$service" "${SERVICES[$service]}"
done

echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}All images built and pushed successfully!${NC}"
echo -e "${GREEN}=========================================${NC}"
echo ""
echo "Your images on Docker Hub:"
for service in "${!SERVICES[@]}"; do
    echo "  - $DOCKER_USERNAME/$PROJECT_NAME-$service:$VERSION"
done
echo ""
echo "To pull images: ./docker-pull.sh"
echo "To deploy with Docker Hub images: docker-compose -f docker-compose.hub.yml up -d"
echo ""
