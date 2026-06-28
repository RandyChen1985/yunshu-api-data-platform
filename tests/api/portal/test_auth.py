import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_get_me_with_valid_key(client: AsyncClient, valid_api_key: str):
    """Test getting current user info with valid API key"""
    response = await client.get(
        "/api/portal/auth/me",
        headers={"X-API-Key": valid_api_key}
    )
    assert response.status_code == 200
    res_json = response.json()
    assert res_json["status"] == "success"
    data = res_json["data"]
    assert "user_id" in data
    assert "user_name" in data
    assert "role" in data
    assert data["status"] == "active"

@pytest.mark.asyncio
async def test_get_me_with_admin_key(client: AsyncClient, admin_api_key: str):
    """Test getting admin user info"""
    response = await client.get(
        "/api/portal/auth/me",
        headers={"X-API-Key": admin_api_key}
    )
    assert response.status_code == 200
    res_json = response.json()
    assert res_json["status"] == "success"
    data = res_json["data"]
    assert data["role"] == "admin"
    assert data["user_name"] == "test_admin"

@pytest.mark.asyncio
async def test_get_me_without_key(client: AsyncClient):
    """Test that request without API key fails"""
    response = await client.get("/api/portal/auth/me")
    assert response.status_code == 401
    assert "Missing API Key" in response.json()["message"]

@pytest.mark.asyncio
async def test_get_me_with_invalid_key(client: AsyncClient):
    """Test that invalid API key fails"""
    response = await client.get(
        "/api/portal/auth/me",
        headers={"X-API-Key": "invalid_key_12345"}
    )
    assert response.status_code == 401
    assert "Invalid API Key" in response.json()["message"]

@pytest.mark.asyncio
async def test_admin_login_success(client: AsyncClient, admin_api_key: str):
    """Test admin login with correct credentials and check for API key masking"""
    response = await client.post(
        "/api/portal/auth/login",
        json={
            "api_key": admin_api_key
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "data" in data
    assert data["data"]["user_name"] == "test_admin"
    assert data["data"]["role"] == "admin"
    
    # Check for API key masking (should not return full key)
    returned_key = data["data"].get("api_key")
    assert returned_key is not None
    assert returned_key != admin_api_key
    assert "..." in returned_key

@pytest.mark.asyncio
async def test_admin_login_with_wrong_key(client: AsyncClient):
    """Test admin login with wrong API key"""
    response = await client.post(
        "/api/portal/auth/login",
        json={
            "api_key": "wrong_key"
        }
    )
    assert response.status_code == 401
    assert "Invalid credentials" in response.json()["message"]

@pytest.mark.asyncio
async def test_change_password_validation(client: AsyncClient, admin_api_key: str):
    """
    Test the smart password change validation logic.
    """
    headers = {"X-API-Key": admin_api_key}
    
    # 1. Try to set/change password
    # First attempt might be setting it for the first time or changing existing
    response = await client.post(
        "/api/portal/auth/change-password",
        json={"new_password": "new_secure_password_123"},
        headers=headers
    )
    
    # If it failed with 400 because a password already exists, then we verify that it requires old_password
    if response.status_code == 400:
        data = response.json()
        error_msg = data.get("message", "") or str(data.get("detail", ""))
        assert "需要提供旧密码" in error_msg
    else:
        assert response.status_code == 200
        
        # Now that a password IS set, try to change it again WITHOUT old_password (should fail)
        response = await client.post(
            "/api/portal/auth/change-password",
            json={"new_password": "another_password_456"},
            headers=headers
        )
        assert response.status_code == 400
        data = response.json()
        error_msg = data.get("message", "") or str(data.get("detail", ""))
        assert "需要提供旧密码" in error_msg

    # 2. Try with WRONG old_password (should fail)
    response = await client.post(
        "/api/portal/auth/change-password",
        json={
            "old_password": "wrong_old_password",
            "new_password": "another_password_456"
        },
        headers=headers
    )
    assert response.status_code == 400
    data = response.json()
    error_msg = data.get("message", "") or str(data.get("detail", ""))
    assert "验证失败" in error_msg