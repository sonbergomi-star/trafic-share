import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_balance(authenticated_client: AsyncClient):
    """Test getting user balance"""
    response = await authenticated_client.get("/api/balance")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "balance_usd" in data["data"]


@pytest.mark.asyncio
async def test_refresh_balance(authenticated_client: AsyncClient):
    """Test refreshing balance"""
    response = await authenticated_client.post("/api/balance/refresh")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"


@pytest.mark.asyncio
async def test_get_transactions(authenticated_client: AsyncClient):
    """Test getting transaction history"""
    response = await authenticated_client.get("/api/balance/transactions")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "transactions" in data["data"]
