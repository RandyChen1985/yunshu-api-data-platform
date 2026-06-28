
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_test_connection_admin_success(client: AsyncClient, admin_api_key: str):
    """Test database connection check as admin"""
    # Only redis is supported now
    response = await client.post(
        "/api/portal/system/test-connection/redis",
        headers={"X-API-Key": admin_api_key}
    )
    # 200 is success, 400 is disabled
    assert response.status_code in [200, 400]
    data = response.json()
    assert "status" in data
    assert "logs" in data

@pytest.mark.asyncio
async def test_test_connection_forbidden_for_regular_user(client: AsyncClient, valid_api_key: str):
    """Test that regular users cannot access connection diagnostics"""
    response = await client.post(
        "/api/portal/system/test-connection/clickhouse",
        headers={"X-API-Key": valid_api_key}
    )
    assert response.status_code == 403
    # After RBAC upgrade, message is "Permission denied: Required 'element:config:save'"
    assert "Permission denied" in response.json()["message"]

@pytest.mark.asyncio
async def test_test_connection_unauthorized(client: AsyncClient):
    """Test access without API Key"""
    response = await client.post("/api/portal/system/test-connection/clickhouse")
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_test_connection_invalid_component(client: AsyncClient, admin_api_key: str):
    """Test invalid component name"""
    response = await client.post(
        "/api/portal/system/test-connection/mysql",  # Not supported via this specific API yet
        headers={"X-API-Key": admin_api_key}
    )
    assert response.status_code == 400
    assert "Unknown component" in response.json()["message"]
