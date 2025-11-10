#!/bin/bash

# Colors
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "========================================="
echo "Text Summarization System - View Logs"
echo "========================================="
echo ""

if [ -z "$1" ]; then
    echo -e "${BLUE}Available services:${NC}"
    echo ""
    echo "Infrastructure:"
    echo "  - zookeeper"
    echo "  - kafka"
    echo "  - schema-registry"
    echo "  - redpanda-console"
    echo ""
    echo "Core Services:"
    echo "  - algo-control"
    echo "  - app-process"
    echo ""
    echo "Router Services:"
    echo "  - root-kafka"
    echo "  - single-kafka"
    echo "  - multi-kafka"
    echo ""
    echo "Algorithm Services:"
    echo "  - textrank, lexrank, lsa"
    echo "  - m-textrank, m-lexrank, m-lsa"
    echo ""
    echo "Additional:"
    echo "  - clustering"
    echo ""
    echo "Usage: ./docker-logs.sh [service-name]"
    echo "Example: ./docker-logs.sh textrank"
    echo ""
    echo "Or view all logs:"
    echo "  docker-compose logs -f"
else
    echo -e "${BLUE}Viewing logs for: $1${NC}"
    echo ""
    docker-compose logs -f --tail=100 $1
fi
