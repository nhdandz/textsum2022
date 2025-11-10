#!/bin/bash

# Test API script for textsum2022
# Usage: ./test_api.sh [pdf_file]

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Load HOST_IP from .env
if [ -f .env ]; then
    export $(grep "^HOST_IP=" .env | xargs)
fi

# Default to localhost if HOST_IP not set
HOST_IP=${HOST_IP:-localhost}
API_URL="http://${HOST_IP}:9980/get_content"

echo -e "${YELLOW}=== TextSum2022 API Test ===${NC}"
echo -e "API URL: ${API_URL}"
echo ""

# Test 1: Simple test with sample PDF
echo -e "${YELLOW}Test 1: Simple PDF (Hello World)${NC}"
curl -s -X POST "${API_URL}" \
  -H "Content-Type: application/json" \
  -d '{
    "data": [{
      "documents_id": "test_simple",
      "encode": "JVBERi0xLjQKJeLjz9MKNCAwIG9iago8PC9UeXBlL0NhdGFsb2cvUGFnZXMgMiAwIFI+PgplbmRvYmoKMiAwIG9iago8PC9UeXBlL1BhZ2VzL0tpZHNbMyAwIFJdL0NvdW50IDE+PgplbmRvYmoKMyAwIG9iago8PC9UeXBlL1BhZ2UvTWVkaWFCb3hbMCAwIDYxMiA3OTJdL1Jlc291cmNlczw8L0ZvbnQ8PC9GMSA1IDAgUj4+Pj4vQ29udGVudHMgNCAwIFI+PgplbmRvYmoKNCAwIG9iago8PC9MZW5ndGggNDQ+PgpzdHJlYW0KQlQKL0YxIDI0IFRmCjEwMCAzMDAgVGQKKEhlbGxvIFdvcmxkKSBUagpFVAplbmRzdHJlYW0KZW5kb2JqCjUgMCBvYmoKPDwvVHlwZS9Gb250L1N1YnR5cGUvVHlwZTEvQmFzZUZvbnQvSGVsdmV0aWNhPj4KZW5kb2JqCnhyZWYKMCA2CjAwMDAwMDAwMDAgNjU1MzUgZiAKMDAwMDAwMDAxNSAwMDAwMCBuIAowMDAwMDAwMDY0IDAwMDAwIG4gCjAwMDAwMDAxMjEgMDAwMDAgbiAKMDAwMDAwMDIyNiAwMDAwMCBuIAowMDAwMDAwMzE5IDAwMDAwIG4gCnRyYWlsZXIKPDwvU2l6ZSA2L1Jvb3QgMSAwIFI+PgpzdGFydHhyZWYKMzg4CiUlRU9GCg==",
      "file_type": 1,
      "page_from": 0,
      "page_to": 5
    }]
  }' | jq '.'

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Test 1 passed${NC}\n"
else
    echo -e "${RED}✗ Test 1 failed${NC}\n"
fi

# Test 2: With real PDF file (if provided)
if [ -n "$1" ] && [ -f "$1" ]; then
    echo -e "${YELLOW}Test 2: Real PDF file ($1)${NC}"
    BASE64_CONTENT=$(base64 -w 0 "$1")

    curl -s -X POST "${API_URL}" \
      -H "Content-Type: application/json" \
      --max-time 300 \
      -d "{
        \"data\": [{
          \"documents_id\": \"test_real_$(date +%s)\",
          \"encode\": \"$BASE64_CONTENT\",
          \"file_type\": 1,
          \"page_from\": 0,
          \"page_to\": 5
        }]
      }" | jq '.'

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Test 2 passed${NC}\n"
    else
        echo -e "${RED}✗ Test 2 failed${NC}\n"
    fi
else
    echo -e "${YELLOW}Test 2 skipped: No PDF file provided${NC}"
    echo -e "Usage: $0 <pdf_file>\n"
fi

# Test 3: Check service status
echo -e "${YELLOW}Test 3: Docker services status${NC}"
docker compose ps | grep -E "app-process|single-kafka"
echo ""

# Test 4: Check recent logs
echo -e "${YELLOW}Test 4: Recent app-process logs${NC}"
docker compose logs --tail=10 app-process
echo ""

echo -e "${YELLOW}=== Test Complete ===${NC}"
