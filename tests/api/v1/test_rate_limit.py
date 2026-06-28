import pytest
import datetime
from httpx import AsyncClient
from app.main import app
from unittest.mock import patch, AsyncMock, MagicMock
from fastapi import status

@pytest.fixture
def mock_auth_service():
    with patch("app.services.auth_service.AuthService.verify_api_key", new_callable=AsyncMock) as mock:
        yield mock

@pytest.fixture
def mock_redis():
    with patch("app.core.redis.get_redis", new_callable=AsyncMock) as mock:
        # Create a mock redis client
        redis_client = AsyncMock()
        mock.return_value = redis_client
        yield redis_client

@pytest.fixture
def mock_system_service():
    with patch("app.services.system_service.SystemService.get_config", new_callable=AsyncMock) as mock:
        yield mock

@pytest.fixture
def mock_resource_access():
    with patch("app.core.dependencies.verify_resource_access", new_callable=AsyncMock) as mock:
        yield mock

@pytest.mark.asyncio
async def test_rate_limit_headers_injection(client: AsyncClient, mock_auth_service, mock_redis, mock_resource_access):
    """验证限流响应头是否正确注入"""
    # 1. Mock Auth
    mock_auth_service.return_value = {
        "user_id": "1",
        "user_name": "test_user",
        "role": "user",
        "user_rate_limit": None,
        "role_rate_limit": None
    }
    
    # 2. Mock Redis Counter
    mock_redis.incr.return_value = 5 # 第 5 次请求
    
    # 3. Request
    response = await client.get(
        "/api/v1/resources/test_resource",
        headers={"X-API-Key": "test_key"}
    )
    
    # 4. Assert Headers
    assert "X-RateLimit-Limit" in response.headers
    assert "X-RateLimit-Remaining" in response.headers
    assert "X-RateLimit-Reset" in response.headers
    assert int(response.headers["X-RateLimit-Limit"]) >= 100 # Default user limit

@pytest.mark.asyncio
async def test_rate_limit_exceeded(client: AsyncClient, mock_auth_service, mock_redis, mock_resource_access):
    """验证超过限流阈值时返回 429"""
    # 1. Mock Auth (Limit 10)
    mock_auth_service.return_value = {
        "user_id": "1",
        "user_name": "test_user",
        "role": "user",
        "user_rate_limit": 10,
        "role_rate_limit": None
    }
    
    # 2. Mock Redis (Current count > Limit)
    mock_redis.incr.return_value = 11
    
    # 3. Request
    response = await client.get(
        "/api/v1/resources/test_resource",
        headers={"X-API-Key": "test_key"}
    )
    
    # 4. Assert 429
    assert response.status_code == 429
    assert "Rate limit exceeded" in response.json()["message"]

@pytest.mark.asyncio
async def test_rate_limit_hierarchical_priority(client: AsyncClient, mock_auth_service, mock_redis, mock_resource_access):
    """验证限流优先级: 用户 > 角色 > 全局"""
    
    # Case: 用户级限流生效
    mock_auth_service.return_value = {
        "user_id": "1", "user_name": "u1", "role": "user",
        "user_rate_limit": 500, "role_rate_limit": 200
    }
    mock_redis.incr.return_value = 1
    
    response = await client.get("/api/v1/resources/test", headers={"X-API-Key": "k1"})
    assert response.headers["X-RateLimit-Limit"] == "500"

    # Case: 角色级限流生效 (用户级为 None)
    mock_auth_service.return_value = {
        "user_id": "2", "user_name": "u2", "role": "user",
        "user_rate_limit": None, "role_rate_limit": 300
    }
    response = await client.get("/api/v1/resources/test", headers={"X-API-Key": "k2"})
    assert response.headers["X-RateLimit-Limit"] == "300"

@pytest.mark.asyncio
async def test_rate_limit_fail_open(client: AsyncClient, mock_auth_service, mock_redis, mock_resource_access):
    """验证 Redis 故障时自动降级 (Fail-Open)"""
    mock_auth_service.return_value = {
        "user_id": "1", "user_name": "u1", "role": "user",
        "user_rate_limit": None, "role_rate_limit": None
    }
    
    # Mock Redis 抛出异常
    mock_redis.incr.side_effect = Exception("Redis Down")
    
    # 请求仍应成功 (因为 Fail-Open)
    response = await client.get(
        "/api/v1/resources/test_resource",
        headers={"X-API-Key": "test_key"}
    )
    
    # 虽然业务成功，但 Headers 此时不应存在（因为流控逻辑被跳过）
    # 注意：因为 mock_resource_access 的缘故，这儿应该返回 200 或 404 (如果 adapter 没 mock)
    # 我们只关心它是不是 429
    assert response.status_code != 429
    assert "X-RateLimit-Limit" not in response.headers

@pytest.mark.asyncio
async def test_rate_limit_global_switch(client: AsyncClient, mock_auth_service, mock_redis, mock_resource_access):
    """验证全局流控开关"""
    with patch("app.services.system_service.SystemService.get_bool_config", new_callable=AsyncMock) as mock_cfg:
        # 1. 关闭总开关
        mock_cfg.return_value = False
        mock_auth_service.return_value = {"user_id": "1", "user_name": "u1", "role": "user"}
        
        response = await client.get("/api/v1/resources/test", headers={"X-API-Key": "k1"})
        
        assert response.status_code != 429
        # 开关关闭时，不应有限流头，也不应调用 Redis
        assert "X-RateLimit-Limit" not in response.headers
        assert not mock_redis.incr.called
