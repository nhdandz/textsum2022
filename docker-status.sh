#!/bin/bash

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "========================================="
echo "Text Summarization System - Status"
echo "========================================="
echo ""

echo -e "${BLUE}Container Status:${NC}"
docker-compose ps

echo ""
echo -e "${BLUE}Resource Usage:${NC}"
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}" \
    $(docker-compose ps -q)

echo ""
echo -e "${BLUE}API Health Checks:${NC}"

check_api() {
    url=$1
    name=$2

    if curl -s -f "$url" > /dev/null 2>&1; then
        echo -e "  ${GREEN}✓${NC} $name: $url"
    else
        echo -e "  ${RED}✗${NC} $name: $url (not responding)"
    fi
}

check_api "http://localhost:6789/" "Algorithm Control"
check_api "http://localhost:9980/" "Document Processing"
check_api "http://localhost:9400/" "Text Clustering"
check_api "http://localhost:8088/" "Kafka UI"

echo ""
