import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.services.auth_service import AuthService
from app.core.database import get_db_connection
from unittest.mock import patch, AsyncMock, MagicMock

@pytest.fixture
def mock_auth_service():
    """Mock AuthService verify_api_key to avoid real DB/Redis interaction"""
    with patch("app.services.auth_service.AuthService.verify_api_key", new_callable=AsyncMock) as mock:
        yield mock

@pytest.fixture
def mock_clickhouse_adapter():
    """Mock ClickHouseAdapter execute to avoid real DB interaction"""
    with patch("app.services.data_adapter.clickhouse.ClickHouseAdapter.execute", new_callable=AsyncMock) as mock:
        from app.services.data_adapter.models import ResultSet
        # Default mock return value
        mock.return_value = ResultSet(items=[], total=0, page=1, size=20, pages=0)
        yield mock

@pytest.fixture
def mock_rate_limit():
    """Mock rate limit to avoid Redis interaction"""
    with patch("app.core.dependencies.check_rate_limit", new_callable=AsyncMock) as mock:
        yield mock

    @pytest.mark.asyncio
    async def test_permission_denied_for_regular_user(client: AsyncClient, mock_auth_service, mock_rate_limit):
        """Test regular user accessing unauthorized resource"""
        # Use a user that actually exists in DB to satisfy FK constraints
        async with get_db_connection() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("SELECT id FROM api_users WHERE user_name = 'test_user'")
                row = await cursor.fetchone()
                user_id = str(row[0]) if row else "1"
        
        mock_auth_service.return_value = {
            "user_id": user_id,
            "user_name": "test_user",
            "role": "user",
            "status": 1
        }
        
        # User has permission for "test_donghuan_real_metrics" but NOT "test_donghuan_events"
        response = await client.get(
            "/api/v1/resources/test_donghuan_events",
            headers={"X-API-Key": "any_key_mocked"}
        )
        
        assert response.status_code == 403
        assert "Access denied" in response.json()["message"]
@pytest.mark.asyncio
async def test_permission_allowed_for_regular_user(client: AsyncClient, mock_auth_service, mock_clickhouse_adapter, mock_rate_limit):
    """Test regular user accessing authorized resource"""
    # Setup Regular User with permissions
    async with get_db_connection() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("SELECT id FROM api_users WHERE user_name = 'test_user'")
            row = await cursor.fetchone()
            user_id = str(row[0]) if row else "2"
    
    mock_auth_service.return_value = {
        "user_id": user_id,
        "user_name": "test_user",
        "role": "user",
        "status": 1
    }

    # Accessing allowed resource
    response = await client.get(
        "/api/v1/resources/test_donghuan_real_metrics",
        headers={"X-API-Key": "any_key_mocked"}
    )
    
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_admin_access_any_resource(client: AsyncClient, mock_auth_service, mock_clickhouse_adapter, mock_rate_limit):
    """Test admin accessing any resource regardless of permissions field"""
    # Setup Admin User
    async with get_db_connection() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("SELECT id FROM api_users WHERE user_name = 'test_admin'")
            row = await cursor.fetchone()
            admin_id = str(row[0]) if row else "1"

    mock_auth_service.return_value = {
        "user_id": admin_id,
        "user_name": "test_admin",
        "role": "admin",
        "status": 1
    }

    # Access resource that regular user would be denied
    response = await client.get(
        "/api/v1/resources/test_donghuan_events",
        headers={"X-API-Key": "any_key_mocked"}
    )
    
    assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_query_permission_denied(client: AsyncClient, mock_auth_service, mock_rate_limit):
        """Test generic query endpoint permission check"""
        # Setup Regular User
        async with get_db_connection() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("SELECT id FROM api_users WHERE user_name = 'test_user'")
                row = await cursor.fetchone()
                user_id = str(row[0]) if row else "2"

        mock_auth_service.return_value = {
            "user_id": user_id,
            "user_name": "test_user",
            "role": "user",
            "status": 1
        }

        response = await client.post(
            "/api/v1/query/",
            json={"resource": "test_donghuan_events"}, # Unauthorized resource
            headers={"X-API-Key": "any_key_mocked"}
        )
        
        assert response.status_code == 403
        assert "Access denied" in response.json()["message"]
@pytest.mark.asyncio
async def test_query_permission_allowed(client: AsyncClient, mock_auth_service, mock_clickhouse_adapter, mock_rate_limit):
    """Test generic query endpoint permission allowed"""
    # Setup Regular User
    async with get_db_connection() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("SELECT id FROM api_users WHERE user_name = 'test_user'")
            row = await cursor.fetchone()
            user_id = str(row[0]) if row else "2"

    mock_auth_service.return_value = {
        "user_id": user_id,
        "user_name": "test_user",
        "role": "user",
        "status": 1
    }

    response = await client.post(
        "/api/v1/query/",
        json={"resource": "test_donghuan_real_metrics"}, # Authorized resource
        headers={"X-API-Key": "any_key_mocked"}
    )
    
    assert response.status_code == 200