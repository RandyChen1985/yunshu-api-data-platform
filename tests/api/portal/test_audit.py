import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_admin_can_view_all_logs(client: AsyncClient, admin_api_key: str):
    """Test that admin can view all audit logs"""
    response = await client.get(
        "/api/portal/audit/logs?page=1&size=10",
        headers={"X-API-Key": admin_api_key}
    )
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "items" in data
    assert isinstance(data["items"], list)
    assert data["page"] == 1
    assert data["size"] == 10

@pytest.mark.asyncio
async def test_user_can_only_view_own_logs(client: AsyncClient, valid_api_key: str):
    """Test that regular user can only view their own logs"""
    response = await client.get(
        "/api/portal/audit/logs?page=1&size=10",
        headers={"X-API-Key": valid_api_key}
    )
    assert response.status_code == 200
    data = response.json()
    # Regular user should only see their own logs
    # All logs should belong to test_user
    for log in data["items"]:
        if "user_name" in log:
            assert log["user_name"] == "test_user"

@pytest.mark.asyncio
async def test_admin_can_filter_by_username(client: AsyncClient, admin_api_key: str):
    """Test that admin can filter logs by username"""
    response = await client.get(
        "/api/portal/audit/logs?user_name=test_admin",
        headers={"X-API-Key": admin_api_key}
    )
    assert response.status_code == 200
    data = response.json()
    # All returned logs should be for admin user
    for log in data["items"]:
        assert log["user_name"] == "test_admin"

@pytest.mark.asyncio
async def test_user_filter_is_ignored(client: AsyncClient, valid_api_key: str):
    """Test that regular user's filter is ignored (forced to own logs)"""
    # Try to filter by another user
    response = await client.get(
        "/api/portal/audit/logs?user_name=test_admin",
        headers={"X-API-Key": valid_api_key}
    )
    assert response.status_code == 200
    data = response.json()
    # Should still only see own logs, not admin's
    for log in data["items"]:
        if "user_name" in log:
            assert log["user_name"] == "test_user"

@pytest.mark.asyncio
async def test_pagination_works(client: AsyncClient, admin_api_key: str):
    """Test that pagination works correctly"""
    response = await client.get(
        "/api/portal/audit/logs?page=1&size=5",
        headers={"X-API-Key": admin_api_key}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 1
    assert data["size"] == 5
    assert len(data["items"]) <= 5

@pytest.mark.asyncio
async def test_logs_without_auth_fails(client: AsyncClient):
    """Test that accessing logs without API key fails"""
    response = await client.get("/api/portal/audit/logs")
    assert response.status_code == 401
