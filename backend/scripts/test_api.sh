#!/bin/bash
# Test API endpoints

API_URL="http://113.30.191.89/api"

echo "Testing API endpoints..."
echo "======================="

# Test health check
echo -e "\n1. Health Check:"
curl -s "${API_URL}/health" | jq .

# Test Telegram auth (mock)
echo -e "\n2. Telegram Auth (mock):"
curl -s -X POST "${API_URL}/auth/telegram" \
  -H "Content-Type: application/json" \
  -d '{
    "id": 123456789,
    "first_name": "Test",
    "username": "testuser",
    "auth_date": 1234567890,
    "hash": "mock_hash"
  }' | jq .

# Save token for subsequent requests
TOKEN=$(curl -s -X POST "${API_URL}/auth/telegram" \
  -H "Content-Type: application/json" \
  -d '{
    "id": 123456789,
    "first_name": "Test",
    "username": "testuser",
    "auth_date": 1234567890,
    "hash": "mock_hash"
  }' | jq -r .access_token)

echo -e "\nToken: $TOKEN"

# Test dashboard (requires auth)
echo -e "\n3. Dashboard:"
curl -s -X GET "${API_URL}/dashboard" \
  -H "Authorization: Bearer $TOKEN" | jq .

# Test balance
echo -e "\n4. Balance:"
curl -s -X GET "${API_URL}/balance" \
  -H "Authorization: Bearer $TOKEN" | jq .

# Test statistics
echo -e "\n5. Statistics:"
curl -s -X GET "${API_URL}/stats?period=week" \
  -H "Authorization: Bearer $TOKEN" | jq .

echo -e "\n======================="
echo "API testing completed!"
