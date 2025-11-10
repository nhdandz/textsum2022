#!/bin/bash

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "========================================="
echo "Docker Hub Username Setup"
echo "========================================="
echo ""

# Prompt for username
read -p "Enter your Docker Hub username: " DOCKER_USERNAME

if [ -z "$DOCKER_USERNAME" ]; then
    echo -e "${YELLOW}Username cannot be empty!${NC}"
    exit 1
fi

# Confirm
echo ""
echo -e "${BLUE}You entered: $DOCKER_USERNAME${NC}"
read -p "Is this correct? (y/n): " confirm

if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
    echo "Setup cancelled."
    exit 0
fi

echo ""
echo -e "${BLUE}Setting up configuration...${NC}"

# Create .env file
cat > .env << EOF
# Docker Hub Configuration
DOCKER_USERNAME=$DOCKER_USERNAME
VERSION=latest
EOF

echo -e "${GREEN}✓ Created .env file${NC}"

# Update docker-compose.hub.yml
sed -i.bak "s/your-dockerhub-username/$DOCKER_USERNAME/g" docker-compose.hub.yml
echo -e "${GREEN}✓ Updated docker-compose.hub.yml${NC}"

# Update scripts
sed -i.bak "s/your-dockerhub-username/$DOCKER_USERNAME/g" docker-build-and-push.sh
echo -e "${GREEN}✓ Updated docker-build-and-push.sh${NC}"

sed -i.bak "s/your-dockerhub-username/$DOCKER_USERNAME/g" docker-pull.sh
echo -e "${GREEN}✓ Updated docker-pull.sh${NC}"

echo ""
echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}Setup completed successfully!${NC}"
echo -e "${GREEN}=========================================${NC}"
echo ""
echo "Next steps:"
echo "  1. Login to Docker Hub: docker login"
echo "  2. Build and push images: ./docker-build-and-push.sh"
echo "  3. Or deploy from Docker Hub: docker-compose -f docker-compose.hub.yml up -d"
echo ""
