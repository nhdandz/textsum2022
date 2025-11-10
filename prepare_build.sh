#!/bin/bash
# Prepare environment before building Docker images

echo "🔧 Preparing environment for Docker build..."
echo "=" * 60

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found! Creating from .env.example..."
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "✓ Created .env from .env.example"
    else
        echo "HOST_IP=192.168.210.42" > .env
        echo "✓ Created default .env"
    fi
fi

# Copy .env to module directories (for Dockerfile COPY if needed)
echo ""
echo "📋 Copying .env to modules..."
for dir in modules/*/ modules/*/*/; do
    if [ -f "${dir}Dockerfile" ]; then
        cp -f .env "$dir.env" 2>/dev/null
        echo "✓ ${dir}.env"
    fi
done

echo ""
echo "✅ Environment preparation complete!"
echo ""
echo "Next steps:"
echo "  1. Build Docker images: docker-compose build"
echo "  2. Run services: docker-compose up -d"
