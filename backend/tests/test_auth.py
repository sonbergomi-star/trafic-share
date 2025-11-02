import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_telegram_auth(client: AsyncClient, mock_user_data):
    """Test Telegram authentication"""
    response = await client.post("/api/auth/telegram", json=mock_user_data)
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert "user" in data


@pytest.mark.asyncio
async def test_telegram_auth_invalid_data(client: AsyncClient):
    """Test Telegram auth with invalid data"""
    invalid_data = {
        "id": "invalid",
        "first_name": "",
    }
    
    response = await client.post("/api/auth/telegram", json=invalid_data)
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_token_renewal(authenticated_client: AsyncClient):
    """Test token renewal"""
    response = await authenticated_client.post("/api/auth/renew")
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data


@pytest.mark.asyncio
async def test_logout(authenticated_client: AsyncClient):
    """Test logout"""
    response = await authenticated_client.post("/api/auth/logout")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
