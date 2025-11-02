#!/bin/bash

# Deployment script for VPS
# VPS IP: 113.30.191.89
# Username: adminuser

echo "?? Starting deployment..."

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Step 1: Updating system packages...${NC}"
sudo apt-get update && sudo apt-get upgrade -y

echo -e "${YELLOW}Step 2: Installing required packages...${NC}"
sudo apt-get install -y python3 python3-pip python3-venv postgresql postgresql-contrib redis-server nginx git

echo -e "${YELLOW}Step 3: Setting up PostgreSQL...${NC}"
sudo -u postgres psql -c "CREATE DATABASE traffic_db;"
sudo -u postgres psql -c "CREATE USER traffic_user WITH PASSWORD 'your_secure_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE traffic_db TO traffic_user;"

echo -e "${YELLOW}Step 4: Setting up Redis...${NC}"
sudo systemctl enable redis-server
sudo systemctl start redis-server

echo -e "${YELLOW}Step 5: Setting up Python virtual environment...${NC}"
cd /home/adminuser
python3 -m venv venv
source venv/bin/activate

echo -e "${YELLOW}Step 6: Installing Python dependencies...${NC}"
cd /home/adminuser/traffic-platform
pip install -r backend/requirements.txt

echo -e "${YELLOW}Step 7: Setting up environment variables...${NC}"
cp backend/.env.example backend/.env
echo "Please edit backend/.env file with your actual credentials"

echo -e "${YELLOW}Step 8: Creating systemd service...${NC}"
sudo tee /etc/systemd/system/traffic-backend.service > /dev/null <<EOF
[Unit]
Description=Traffic Sharing Platform Backend
After=network.target postgresql.service redis.service

[Service]
User=adminuser
WorkingDirectory=/home/adminuser/traffic-platform/backend
Environment="PATH=/home/adminuser/venv/bin"
ExecStart=/home/adminuser/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always

[Install]
WantedBy=multi-user.target
EOF

echo -e "${YELLOW}Step 9: Setting up Nginx reverse proxy...${NC}"
sudo tee /etc/nginx/sites-available/traffic-platform > /dev/null <<EOF
server {
    listen 80;
    server_name 113.30.191.89;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

sudo ln -s /etc/nginx/sites-available/traffic-platform /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

echo -e "${YELLOW}Step 10: Starting services...${NC}"
sudo systemctl daemon-reload
sudo systemctl enable traffic-backend
sudo systemctl start traffic-backend

echo -e "${GREEN}? Deployment completed!${NC}"
echo -e "${YELLOW}Please:${NC}"
echo "1. Edit backend/.env with your actual credentials"
echo "2. Run database migrations: alembic upgrade head"
echo "3. Restart the service: sudo systemctl restart traffic-backend"
