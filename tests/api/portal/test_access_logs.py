import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_admin_can_view_all_access_logs(client: AsyncClient, admin_api_key: str):
    """Test that admin can view all access logs"""
    response = await client.get(
        "/api/portal/logs/access?limit=10",
        headers={"X-API-Key": admin_api_key}
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

@pytest.mark.asyncio
async def test_user_can_view_own_access_logs(client: AsyncClient, valid_api_key: str):
    """Test that regular user can view their own access logs"""
    response = await client.get(
        "/api/portal/logs/access?limit=10",
        headers={"X-API-Key": valid_api_key}
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # Check that all logs belong to the user
    for log in data:
        assert log["user_name"] == "test_user"

@pytest.mark.asyncio
async def test_access_logs_with_resource_key(client: AsyncClient, admin_api_key: str):
    """Test filtering access logs by resource_key"""
    response = await client.get(
        "/api/portal/logs/access?resource_key=yunshu_rooms&limit=10",
        headers={"X-API-Key": admin_api_key}
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    for log in data:
        assert "yunshu_rooms" in log["endpoint"]

@pytest.mark.asyncio
async def test_access_logs_unauthorized(client: AsyncClient):
    """Test that accessing logs without API key fails"""
    response = await client.get("/api/portal/logs/access")
    assert response.status_code == 401
