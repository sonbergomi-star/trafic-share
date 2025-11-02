#!/bin/bash

# Setup SSL certificate using Let's Encrypt
# Run this on VPS after domain is configured

set -e

echo "?? Setting up SSL certificate..."

DOMAIN="113.30.191.89"
EMAIL="admin@example.com"  # Change this

# Install certbot
if ! command -v certbot &> /dev/null; then
    echo "?? Installing certbot..."
    sudo apt-get update
    sudo apt-get install -y certbot python3-certbot-nginx
fi

# Stop nginx temporarily
docker-compose stop nginx

# Get certificate
echo "?? Obtaining SSL certificate..."
sudo certbot certonly --standalone \
    --non-interactive \
    --agree-tos \
    --email $EMAIL \
    --domains $DOMAIN

# Create SSL directory
sudo mkdir -p deployment/ssl

# Copy certificates
sudo cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem deployment/ssl/cert.pem
sudo cp /etc/letsencrypt/live/$DOMAIN/privkey.pem deployment/ssl/key.pem
sudo chown adminuser:adminuser deployment/ssl/*

# Restart nginx with SSL
docker-compose up -d nginx

echo "? SSL certificate installed successfully!"
echo ""
echo "Note: Uncomment HTTPS section in deployment/nginx.conf to enable SSL"
