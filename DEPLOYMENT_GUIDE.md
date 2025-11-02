# Traffic Platform - Deployment Guide

Complete deployment guide for setting up the Traffic Platform on Ubuntu 24.04 VPS.

## Prerequisites

- Ubuntu 24.04 VPS
- IP: 113.30.191.89
- Username: adminuser
- Domain (optional, for SSL)
- SSH access

## Table of Contents

1. [Initial Server Setup](#initial-server-setup)
2. [Install Dependencies](#install-dependencies)
3. [Configure Application](#configure-application)
4. [Deploy with Docker](#deploy-with-docker)
5. [Setup SSL (Optional)](#setup-ssl)
6. [Configure Firewall](#configure-firewall)
7. [Monitoring & Maintenance](#monitoring--maintenance)

---

## Initial Server Setup

### 1. Update System

```bash
sudo apt update && sudo apt upgrade -y
```

### 2. Create Application Directory

```bash
sudo mkdir -p /opt/traffic-platform
sudo chown adminuser:adminuser /opt/traffic-platform
```

### 3. Install Basic Tools

```bash
sudo apt install -y \
    git \
    curl \
    wget \
    vim \
    htop \
    ufw
```

---

## Install Dependencies

### 1. Install Docker

```bash
# Add Docker's official GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Set up Docker repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Add user to docker group
sudo usermod -aG docker adminuser

# Start Docker
sudo systemctl enable docker
sudo systemctl start docker
```

### 2. Install Docker Compose

```bash
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
docker-compose --version
```

---

## Configure Application

### 1. Clone/Upload Project

```bash
cd /opt/traffic-platform
# Upload via scp or git clone
```

### 2. Configure Environment Variables

```bash
cd /opt/traffic-platform
cp backend/.env.example backend/.env
nano backend/.env
```

Update the following values:

```env
# Database
DATABASE_URL=postgresql+asyncpg://postgres:YOUR_STRONG_PASSWORD@db:5432/traffic_platform

# JWT Secret (generate a strong random string)
JWT_SECRET_KEY=YOUR_JWT_SECRET_HERE

# Telegram Bot
TELEGRAM_BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN
TELEGRAM_BOT_USERNAME=YOUR_BOT_USERNAME

# Admin IDs (comma-separated)
ADMIN_IDS=123456789,987654321

# Redis
REDIS_URL=redis://redis:6379/0

# Payment Provider
PAYMENT_PROVIDER_API_KEY=YOUR_PAYMENT_API_KEY

# FCM (Firebase Cloud Messaging)
FCM_SERVER_KEY=YOUR_FCM_SERVER_KEY

# VPS Configuration
VPS_IP=113.30.191.89
```

### 3. Generate Secrets

```bash
# Generate JWT secret
openssl rand -hex 32

# Generate strong database password
openssl rand -base64 32
```

---

## Deploy with Docker

### 1. Build and Start Services

```bash
cd /opt/traffic-platform
docker-compose up -d --build
```

### 2. Check Container Status

```bash
docker-compose ps
docker-compose logs -f backend
```

### 3. Initialize Database

```bash
# Run migrations
docker-compose exec backend alembic upgrade head

# Initialize default data
docker-compose exec backend python scripts/init_db.py

# Create admin user
docker-compose exec backend python scripts/create_admin.py 123456789 admin AdminName
```

### 4. Verify Deployment

```bash
# Check API health
curl http://localhost:8000/api/health

# Check Nginx
curl http://localhost/api/health
```

---

## Setup SSL (Optional)

### 1. Install Certbot

```bash
sudo apt install -y certbot python3-certbot-nginx
```

### 2. Obtain SSL Certificate

```bash
# Stop nginx temporarily
docker-compose stop nginx

# Get certificate
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

# Restart nginx
docker-compose start nginx
```

### 3. Configure Nginx for SSL

```bash
cd /opt/traffic-platform
./deployment/setup-ssl.sh yourdomain.com
```

### 4. Auto-renewal

```bash
# Add cron job for auto-renewal
sudo crontab -e

# Add this line:
0 0 * * * certbot renew --quiet --post-hook "docker-compose -f /opt/traffic-platform/docker-compose.yml restart nginx"
```

---

## Configure Firewall

### 1. Setup UFW

```bash
# Allow SSH
sudo ufw allow 22/tcp

# Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Enable firewall
sudo ufw enable

# Check status
sudo ufw status
```

### 2. Rate Limiting (Optional)

```bash
# Limit SSH connections
sudo ufw limit ssh

# Check logs
sudo tail -f /var/log/ufw.log
```

---

## Monitoring & Maintenance

### 1. View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f nginx

# Last 100 lines
docker-compose logs --tail=100 backend
```

### 2. Restart Services

```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart backend
docker-compose restart nginx
```

### 3. Update Application

```bash
cd /opt/traffic-platform

# Pull latest changes
git pull

# Rebuild and restart
docker-compose up -d --build

# Run migrations if needed
docker-compose exec backend alembic upgrade head
```

### 4. Backup Database

```bash
# Create backup
docker-compose exec db pg_dump -U postgres traffic_platform > backup_$(date +%Y%m%d).sql

# Restore from backup
docker-compose exec -T db psql -U postgres traffic_platform < backup_20240101.sql
```

### 5. Monitor Resources

```bash
# Docker stats
docker stats

# Disk usage
df -h

# Memory usage
free -h

# View running processes
docker-compose top
```

---

## Troubleshooting

### Application Won't Start

1. Check logs: `docker-compose logs backend`
2. Verify environment variables in `.env`
3. Check database connection
4. Ensure all required services are running

### Database Connection Issues

```bash
# Check database container
docker-compose ps db

# Connect to database
docker-compose exec db psql -U postgres -d traffic_platform

# Check connection from backend
docker-compose exec backend python -c "from app.core.database import engine; import asyncio; asyncio.run(engine.connect())"
```

### Nginx/SSL Issues

```bash
# Test nginx configuration
docker-compose exec nginx nginx -t

# Check SSL certificates
sudo certbot certificates

# Reload nginx
docker-compose exec nginx nginx -s reload
```

### High Memory Usage

```bash
# Check container memory
docker stats

# Restart services
docker-compose restart

# Clear unused images/containers
docker system prune -a
```

---

## Security Checklist

- [ ] Changed default database password
- [ ] Generated strong JWT secret
- [ ] Configured firewall (UFW)
- [ ] Setup SSL certificate
- [ ] Configured rate limiting
- [ ] Setup automatic backups
- [ ] Configured monitoring alerts
- [ ] Restricted admin access
- [ ] Updated all system packages

---

## Support

For issues or questions:
- Check logs: `docker-compose logs`
- Review documentation
- Contact system administrator

---

**Last Updated:** 2024-01-01
**Version:** 1.0.0
