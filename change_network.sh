#!/bin/bash

# Script to change network IP for the entire project
# Usage: ./change_network.sh <NEW_IP>

if [ -z "$1" ]; then
    echo "Usage: $0 <NEW_IP>"
    echo "Example: $0 192.168.1.100"
    exit 1
fi

NEW_IP=$1
OLD_IP=$(grep "^HOST_IP=" .env | cut -d'=' -f2)

echo "========================================="
echo "Network IP Change Script"
echo "========================================="
echo "Current IP: $OLD_IP"
echo "New IP: $NEW_IP"
echo ""
read -p "Continue? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 1
fi

echo ""
echo "Step 1: Updating .env file..."
sed -i "s/HOST_IP=$OLD_IP/HOST_IP=$NEW_IP/g" .env
sed -i "s/$OLD_IP/$NEW_IP/g" .env
echo "✓ Updated .env"

echo ""
echo "Step 2: Updating Ollama systemd config (requires sudo)..."
echo "   Adding OLLAMA_HOST=0.0.0.0:11434 to ensure Ollama listens on all interfaces..."
if ! grep -q "OLLAMA_HOST" /etc/systemd/system/ollama.service.d/override.conf 2>/dev/null; then
    echo 'Environment="OLLAMA_HOST=0.0.0.0:11434"' | sudo tee -a /etc/systemd/system/ollama.service.d/override.conf > /dev/null
    echo "✓ Added OLLAMA_HOST config"
else
    echo "✓ OLLAMA_HOST already configured"
fi

echo ""
echo "Step 3: Restarting Ollama service..."
sudo systemctl daemon-reload
sudo systemctl restart ollama
echo "✓ Ollama restarted"

echo ""
echo "Step 4: Restarting Docker containers..."
docker compose down
echo "   Cleaning up old Kafka volume (optional, only if having issues)..."
read -p "   Remove Kafka volume for clean start? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    docker volume rm textsum2022_kafka_data 2>/dev/null || true
    echo "✓ Kafka volume removed"
else
    echo "  Kept existing Kafka volume"
fi

docker compose up -d
echo "✓ Docker containers restarted"

echo ""
echo "========================================="
echo "Network change completed!"
echo "========================================="
echo ""
echo "New configuration:"
echo "  HOST_IP: $NEW_IP"
echo "  Kafka: $NEW_IP:9092"
echo "  Kafka UI: http://$NEW_IP:8080"
echo "  Ollama: http://$NEW_IP:11434"
echo "  Algo Control: http://$NEW_IP:6789"
echo ""
echo "Please verify:"
echo "  1. Check Ollama: curl http://$NEW_IP:11434/api/tags"
echo "  2. Check Kafka: docker logs kafka-1 --tail 20"
echo "  3. Test services: docker compose ps"
echo ""
