import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from unittest.mock import patch, AsyncMock

@pytest.fixture
def mock_auth_service_forbidden():
    """Mock AuthService to throw forbidden error indirectly via permission check"""
    # Actually, we can just trigger a 403 by using a mock user with no permissions
    with patch("app.services.auth_service.AuthService.verify_api_key", new_callable=AsyncMock) as mock:
        mock.return_value = {
            "user_id": "100",
            "user_name": "test_user",
            "role": "user",
            "permissions": {"allowed_resources": []}, # No access
            "status": 1
        }
        yield mock

@pytest.mark.asyncio
async def test_403_error_format(client: AsyncClient, mock_auth_service_forbidden):
    """Test that 403 Forbidden error follows the unified JSON format"""
    # Access a resource without permission
    response = await client.get(
        "/api/v1/resources/donghuan_events",
        headers={"X-API-Key": "valid_but_no_perm"}
    )
    
    assert response.status_code == 403
    data = response.json()
    
    # Check structure
    assert "code" in data
    assert data["code"] == 4031 # ACCESS_DENIED
    assert "message" in data
    assert "Access denied" in data["message"]
    assert "data" in data
    assert data["data"] is None
    assert "timestamp" in data
    assert "trace_id" in data

@pytest.mark.asyncio
async def test_404_error_format(client: AsyncClient):
    """Test that 404 Not Found error follows the unified JSON format"""
    response = await client.get(
        "/api/v1/non-existent-endpoint",
        headers={"X-API-Key": "any_key"} # Auth usually runs before 404 for protected routes, but let's see
    )
    
    # FastAPI returns 404 for unknown routes. 
    # If standard 404 handler is not overridden, it returns {"detail": "Not Found"}
    # But we overrode generic HTTPException handler. 404 is an HTTPException.
    
    assert response.status_code == 404
    data = response.json()
    
    assert "code" in data
    assert data["code"] == 4004 # RESOURCE_NOT_FOUND
    assert "message" in data
    assert data["message"] == "API Not Found"
    assert "timestamp" in data
    assert "trace_id" in data

@pytest.mark.asyncio
async def test_500_error_format(client: AsyncClient):
    """Test that 500 Internal Error follows the unified JSON format"""
    # We need to trigger an unhandled exception.
    # We can mock an endpoint to raise Exception.
    
    # Create a client that doesn't raise exceptions so we can check the 500 response
    async with AsyncClient(transport=ASGITransport(app=app, raise_app_exceptions=False), base_url="http://test") as safe_client:
        with patch("app.services.auth_service.AuthService.verify_api_key", side_effect=Exception("Unexpected Crash")):
            response = await safe_client.get(
                "/api/v1/resources/donghuan_events",
                headers={"X-API-Key": "crash_me"}
            )
            
            assert response.status_code == 500
            data = response.json()
            
            assert "code" in data
            assert data["code"] == 500 # INTERNAL_SERVER_ERROR
            assert "message" in data
            assert data["message"] == "服务器内部错误"
            assert "timestamp" in data
            assert "trace_id" in data
