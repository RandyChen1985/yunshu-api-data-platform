import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_api_key_for_user(client: AsyncClient, admin_api_key: str):
    """Test creating a new API key for regular user"""
    import time
    unique_username = f"api_test_user_{int(time.time())}"
    
    response = await client.post(
        "/api/portal/keys/",
        json={
            "user_name": unique_username,
            "role": "user"
        },
        headers={"X-API-Key": admin_api_key}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["message"] == "success"
    assert data["data"]["user_name"] == unique_username
    assert data["data"]["role"] == "user"
    assert "api_key" in data["data"]
    assert len(data["data"]["api_key"]) > 20

@pytest.mark.asyncio
async def test_create_api_key_duplicate_username(client: AsyncClient, admin_api_key: str):
    """Test that creating duplicate username fails"""
    response = await client.post(
        "/api/portal/keys/",
        json={
            "user_name": "admin",  # Already exists
            "role": "user"
        },
        headers={"X-API-Key": admin_api_key}
    )
    assert response.status_code == 500  # Will fail with duplicate error

@pytest.mark.asyncio
async def test_create_api_key_default_role(client: AsyncClient, admin_api_key: str):
    """Test that default role is 'user' when not specified"""
    import time
    unique_username = f"api_test_default_{int(time.time())}"
    
    response = await client.post(
        "/api/portal/keys/",
        json={
            "user_name": unique_username
            # role not specified, should default to "user"
        },
        headers={"X-API-Key": admin_api_key}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["role"] == "user"
