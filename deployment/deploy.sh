#!/bin/bash

# Traffic Sharing Platform - VPS Deployment Script
# VPS: 113.30.191.89
# User: adminuser

set -e

echo "?? Starting deployment to VPS..."

# Configuration
VPS_IP="113.30.191.89"
VPS_USER="adminuser"
PROJECT_DIR="/home/adminuser/traffic-platform"
REMOTE_PROJECT_DIR="$VPS_USER@$VPS_IP:$PROJECT_DIR"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}?? Step 1: Preparing deployment package...${NC}"

# Create deployment archive
tar -czf traffic-platform.tar.gz \
    --exclude='node_modules' \
    --exclude='.git' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.env' \
    backend/ \
    deployment/ \
    docker-compose.yml \
    README.md

echo -e "${GREEN}? Deployment package created${NC}"

echo -e "${YELLOW}?? Step 2: Uploading to VPS...${NC}"

# Copy files to VPS
scp traffic-platform.tar.gz $VPS_USER@$VPS_IP:/tmp/

echo -e "${GREEN}? Files uploaded${NC}"

echo -e "${YELLOW}?? Step 3: Setting up on VPS...${NC}"

# Execute remote commands
ssh $VPS_USER@$VPS_IP << 'ENDSSH'
    set -e
    
    echo "?? Creating project directory..."
    mkdir -p /home/adminuser/traffic-platform
    cd /home/adminuser/traffic-platform
    
    echo "?? Extracting files..."
    tar -xzf /tmp/traffic-platform.tar.gz
    rm /tmp/traffic-platform.tar.gz
    
    echo "?? Setting up environment..."
    if [ ! -f backend/.env ]; then
        cp backend/.env.example backend/.env
        echo "??  Please edit backend/.env with your configuration"
    fi
    
    echo "?? Installing Docker..."
    if ! command -v docker &> /dev/null; then
        curl -fsSL https://get.docker.com -o get-docker.sh
        sudo sh get-docker.sh
        sudo usermod -aG docker adminuser
        rm get-docker.sh
    fi
    
    echo "?? Installing Docker Compose..."
    if ! command -v docker-compose &> /dev/null; then
        sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        sudo chmod +x /usr/local/bin/docker-compose
    fi
    
    echo "?? Setting up firewall..."
    sudo ufw allow 22/tcp
    sudo ufw allow 80/tcp
    sudo ufw allow 443/tcp
    sudo ufw --force enable
    
    echo "? VPS setup complete!"
ENDSSH

echo -e "${GREEN}? VPS setup complete${NC}"

# Cleanup
rm traffic-platform.tar.gz

echo -e "${GREEN}?? Deployment complete!${NC}"
echo ""
echo "Next steps:"
echo "1. SSH to VPS: ssh $VPS_USER@$VPS_IP"
echo "2. Edit .env file: cd $PROJECT_DIR && nano backend/.env"
echo "3. Start services: cd $PROJECT_DIR && docker-compose up -d"
echo "4. Check logs: docker-compose logs -f"
echo ""
echo "API will be available at: http://$VPS_IP/api"
