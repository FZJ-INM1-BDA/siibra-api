import pytest
from httpx import AsyncClient
from fastapi.testclient import TestClient

from app.app import app

client = TestClient(app)


# Test template returns
# TemplateNotFound Error

@pytest.mark.asyncio
async def test_home():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/")
    # response = client.get("/")
    assert response.status_code == 200
    assert 'Siibra' in str(response.content)


@pytest.mark.asyncio
async def test_stats():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/stats")
    assert response.status_code == 200
    assert 'Siibra - statistics' in str(response.content)
