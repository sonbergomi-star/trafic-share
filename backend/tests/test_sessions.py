import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_start_session(authenticated_client: AsyncClient):
    """Test starting a session"""
    session_data = {
        "ip_address": "1.2.3.4",
        "location": "US",
        "network_type": "wifi"
    }
    
    response = await authenticated_client.post("/api/sessions/start", json=session_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "session_id" in data["data"]


@pytest.mark.asyncio
async def test_stop_session(authenticated_client: AsyncClient):
    """Test stopping a session"""
    # First start a session
    start_response = await authenticated_client.post("/api/sessions/start", json={
        "ip_address": "1.2.3.4",
        "location": "US"
    })
    session_id = start_response.json()["data"]["session_id"]
    
    # Stop the session
    response = await authenticated_client.post(f"/api/sessions/{session_id}/stop")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"


@pytest.mark.asyncio
async def test_report_traffic(authenticated_client: AsyncClient):
    """Test traffic reporting"""
    # Start a session first
    start_response = await authenticated_client.post("/api/sessions/start", json={
        "ip_address": "1.2.3.4",
        "location": "US"
    })
    session_id = start_response.json()["data"]["session_id"]
    
    # Report traffic
    report_data = {
        "session_id": session_id,
        "cumulative_mb": 10.5,
        "delta_mb": 2.5
    }
    
    response = await authenticated_client.post("/api/sessions/report", json=report_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"


@pytest.mark.asyncio
async def test_get_session_history(authenticated_client: AsyncClient):
    """Test getting session history"""
    response = await authenticated_client.get("/api/sessions/history")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "sessions" in data["data"]
