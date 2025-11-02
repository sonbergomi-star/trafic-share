import pytest
from httpx import AsyncClient

from app.main import create_app


@pytest.mark.asyncio
async def test_health_endpoint():
    app = create_app()
    async with AsyncClient(app=app, base_url="http://testserver") as ac:
        response = await ac.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
