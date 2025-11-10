#!/bin/bash

# Docker Hub Configuration
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
echo "Pull Images from Docker Hub"
echo "========================================="
echo ""

# Define services
SERVICES=(
    "algo-control"
    "root-kafka"
    "single-kafka"
    "single-texrank"
    "multi-multexrank"
    "text-similarity"
)

# Function to pull an image
pull_image() {
    local service_name=$1
    local image_name="$DOCKER_USERNAME/$PROJECT_NAME-$service_name:$VERSION"

    echo -e "${BLUE}Pulling $image_name...${NC}"
    docker pull "$image_name"

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Pull successful: $image_name${NC}"
    else
        echo -e "${RED}✗ Failed to pull: $image_name${NC}"
        return 1
    fi

    echo ""
}

# Pull all services
echo -e "${BLUE}Pulling all service images...${NC}"
echo ""

for service in "${SERVICES[@]}"; do
    pull_image "$service"
done

echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}All images pulled successfully!${NC}"
echo -e "${GREEN}=========================================${NC}"
echo ""
echo "To start services: docker-compose -f docker-compose.hub.yml up -d"
echo ""
