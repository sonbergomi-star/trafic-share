import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_withdraw_insufficient_balance(authenticated_client: AsyncClient):
    """Test withdraw with insufficient balance"""
    withdraw_data = {
        "amount_usd": 1000.0,
        "wallet_address": "0x1234567890123456789012345678901234567890"
    }
    
    response = await authenticated_client.post("/api/withdraw/create", json=withdraw_data)
    
    # Should fail due to insufficient balance
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_create_withdraw_invalid_address(authenticated_client: AsyncClient):
    """Test withdraw with invalid wallet address"""
    withdraw_data = {
        "amount_usd": 2.0,
        "wallet_address": "invalid_address"
    }
    
    response = await authenticated_client.post("/api/withdraw/create", json=withdraw_data)
    
    # Should fail due to invalid address
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_create_withdraw_below_minimum(authenticated_client: AsyncClient):
    """Test withdraw below minimum amount"""
    withdraw_data = {
        "amount_usd": 0.5,  # Below $1.39 minimum
        "wallet_address": "0x1234567890123456789012345678901234567890"
    }
    
    response = await authenticated_client.post("/api/withdraw/create", json=withdraw_data)
    
    # Should fail due to amount below minimum
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_get_withdraw_history(authenticated_client: AsyncClient):
    """Test getting withdrawal history"""
    response = await authenticated_client.get("/api/withdraw/history")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "withdrawals" in data["data"]
