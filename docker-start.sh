#!/bin/bash

echo "========================================="
echo "Text Summarization System - Docker Start"
echo "========================================="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check if service is healthy
check_service() {
    service_name=$1
    max_wait=$2
    echo -e "${BLUE}Waiting for $service_name to be ready...${NC}"

    for i in $(seq 1 $max_wait); do
        if docker-compose ps $service_name | grep -q "Up"; then
            echo -e "${GREEN}✓ $service_name is ready${NC}"
            return 0
        fi
        echo -n "."
        sleep 1
    done

    echo -e "${YELLOW}⚠ $service_name might not be fully ready yet${NC}"
    return 1
}

# Step 1: Start Infrastructure
echo -e "\n${BLUE}Step 1: Starting Infrastructure Services...${NC}"
docker-compose up -d zookeeper
check_service "zookeeper" 30

docker-compose up -d kafka
check_service "kafka" 60

docker-compose up -d schema-registry redpanda-console
check_service "schema-registry" 30

# Step 2: Start Core Services
echo -e "\n${BLUE}Step 2: Starting Core Services...${NC}"
docker-compose up -d algo-control app-process
check_service "algo-control" 20
check_service "app-process" 20

# Step 3: Start Kafka Routers
echo -e "\n${BLUE}Step 3: Starting Kafka Router Services...${NC}"
docker-compose up -d root-kafka single-kafka multi-kafka
sleep 5

# Step 4: Start Algorithm Services
echo -e "\n${BLUE}Step 4: Starting Algorithm Services...${NC}"
docker-compose up -d textrank lexrank lsa
docker-compose up -d m-textrank m-lexrank m-lsa
docker-compose up -d clustering

echo -e "\n${GREEN}=========================================${NC}"
echo -e "${GREEN}All services started successfully!${NC}"
echo -e "${GREEN}=========================================${NC}"
echo ""
echo "Service URLs:"
echo "  - Algorithm Control: http://localhost:6789"
echo "  - Document Processing: http://localhost:9980"
echo "  - Text Clustering: http://localhost:9400"
echo "  - Kafka UI (Redpanda): http://localhost:8088"
echo ""
echo "To view logs: docker-compose logs -f"
echo "To stop all: docker-compose down"
echo ""
