#!/bin/bash

# Stop Traffic Sharing Platform services

set -e

echo "?? Stopping Traffic Sharing Platform..."

docker-compose stop

echo "? Services stopped"
echo ""
echo "To start again: ./deployment/start.sh"
echo "To remove containers: docker-compose down"
