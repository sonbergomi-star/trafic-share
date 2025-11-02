#!/bin/bash

# Start Traffic Sharing Platform services on VPS

set -e

echo "?? Starting Traffic Sharing Platform..."

# Check if .env exists
if [ ! -f backend/.env ]; then
    echo "??  Error: backend/.env file not found!"
    echo "Please create it from backend/.env.example"
    exit 1
fi

# Pull latest images
echo "?? Pulling Docker images..."
docker-compose pull

# Build backend
echo "?? Building backend..."
docker-compose build backend

# Start services
echo "?? Starting services..."
docker-compose up -d

# Wait for services to be healthy
echo "? Waiting for services to be ready..."
sleep 10

# Check health
echo "?? Checking service health..."
docker-compose ps

# Show logs
echo ""
echo "?? Recent logs:"
docker-compose logs --tail=50

echo ""
echo "? All services started successfully!"
echo ""
echo "Service URLs:"
echo "  Backend API: http://113.30.191.89/api"
echo "  Health check: http://113.30.191.89/health"
echo "  API Docs: http://113.30.191.89/docs"
echo ""
echo "Useful commands:"
echo "  View logs: docker-compose logs -f"
echo "  Stop services: docker-compose stop"
echo "  Restart services: docker-compose restart"
echo "  View status: docker-compose ps"
