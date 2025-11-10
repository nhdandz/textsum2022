#!/bin/bash

echo "========================================="
echo "Text Summarization System - Docker Stop"
echo "========================================="
echo ""

# Colors
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Stopping all services...${NC}"
docker-compose down

echo -e "\n${RED}All services stopped.${NC}"
echo ""
echo "To start again: ./docker-start.sh"
echo "To remove volumes: docker-compose down -v"
echo ""
