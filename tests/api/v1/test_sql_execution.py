import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from fastapi import HTTPException
from app.core.database import get_db_connection

# Mock Adapter Response
MOCK_DATA = {
    "columns": [{"name": "id", "type": "UInt64"}, {"name": "name", "type": "String"}],
    "items": [[1, "Alice"], [2, "Bob"]]
}

@pytest.fixture
async def setup_permission(valid_api_key):
    """Grant system.sql.execute permission AND granular DS permissions to test user"""
    async with get_db_connection() as conn:
        async with conn.cursor() as cursor:
            # Get User ID
            await cursor.execute("SELECT id FROM api_users WHERE user_name = 'test_user'")
            row = await cursor.fetchone()
            user_id = row[0]
            
            # Insert Resource Meta first (Foreign Key Constraint)
            await cursor.execute(
                "INSERT IGNORE INTO sys_resource_meta (resource_key, resource_name, resource_group, status) VALUES ('system.sql.execute', 'SQL Execute', 'System', 1)"
            )

            # Insert Permissions
            # 1. Global Resource Perm
            await cursor.execute(
                "INSERT IGNORE INTO sys_user_resources (user_id, resource_key) VALUES (%s, 'system.sql.execute')", 
                (user_id,)
            )
            # 2. DataSource Perm (mock_source)
            await cursor.execute(
                "INSERT INTO sys_ui_permissions (user_id, perm_type, perm_code) VALUES (%s, 'datasource', 'ds:mock_source')",
                (user_id,)
            )
            # 3. Table Perm (ALL)
            await cursor.execute(
                "INSERT INTO sys_ui_permissions (user_id, perm_type, perm_code) VALUES (%s, 'data_table', 'ds:mock_source:table:*')",
                (user_id,)
            )
            await conn.commit()
            
            # Invalidate Cache
            from app.services.permission_service import PermissionService
            await PermissionService.invalidate_user_cache(user_id)
            
            return user_id

@pytest.mark.asyncio
async def test_execute_sql_no_permission(client, valid_api_key):
    """Test 403 Forbidden when user lacks permission"""
    # Ensure no permission
    async with get_db_connection() as conn:
        async with conn.cursor() as cursor:
             await cursor.execute("DELETE FROM sys_user_resources WHERE resource_key = 'system.sql.execute'")
             await conn.commit()

    resp = await client.post(
        "/api/v1/sql/execute",
        headers={"X-API-Key": valid_api_key},
        json={
            "data_source": 1,
            "sql": "SELECT * FROM users"
        }
    )
    assert resp.status_code == 403
    assert "Permission Denied" in resp.json()["message"]

@pytest.mark.asyncio
async def test_execute_sql_unsafe(client, valid_api_key, setup_permission):
    """Test 400 Bad Request for unsafe SQL"""
    # Mock data source to avoid 404
    with patch("app.api.v1.endpoints.sql_execution.DataSourceService.get_datasource", new_callable=AsyncMock) as mock_get_ds, \
         patch("app.api.v1.endpoints.sql_execution.get_adapter", new_callable=AsyncMock) as mock_get_adapter:

        mock_get_ds.return_value = MagicMock(id=1, source_name="mock_source")
        
        # Mock adapter
        from unittest.mock import MagicMock as StdMagicMock
        from app.services.data_adapter.base import SQLSafetyError
        mock_adapter = StdMagicMock()
        # Mock _validate_sql_safety to raise SQLSafetyError like a real adapter would
        mock_adapter._validate_sql_safety.side_effect = SQLSafetyError("SQL is forbidden")
        mock_adapter.execute_sql = AsyncMock() 
        mock_get_adapter.return_value = mock_adapter

        resp = await client.post(
            "/api/v1/sql/execute",
            headers={"X-API-Key": valid_api_key},
            json={
                "data_source": 1,
                "sql": "DELETE FROM users WHERE id = 1"
            }
        )
        assert resp.status_code == 400
        assert "SQL is forbidden" in resp.json()["detail"]

@pytest.mark.asyncio
async def test_execute_sql_success(client, valid_api_key, setup_permission):
    """Test 200 OK with mocked adapter"""
    with patch("app.api.v1.endpoints.sql_execution.get_adapter", new_callable=AsyncMock) as mock_get_adapter:
        # Mock Adapter Instance
        from unittest.mock import MagicMock as StdMagicMock
        mock_adapter = StdMagicMock()
        mock_adapter.execute_sql = AsyncMock()
        mock_adapter.execute_sql.return_value = MOCK_DATA
        mock_get_adapter.return_value = mock_adapter
        
        # Mock DataSourceService
        with patch("app.api.v1.endpoints.sql_execution.DataSourceService.get_datasource", new_callable=AsyncMock) as mock_get_ds:
             mock_get_ds.return_value = MagicMock(id=999, source_name="mock_source")
             
             resp = await client.post(
                 "/api/v1/sql/execute",
                 headers={"X-API-Key": valid_api_key},
                 json={
                     "data_source": 999,
                     "sql": "SELECT * FROM users"
                 }
             )
             
             assert resp.status_code == 200
             data = resp.json()["data"]
             assert data["items"][0][1] == "Alice"
             
             # Verify LIMIT enforcement
             call_args = mock_adapter.execute_sql.call_args
             executed_sql = call_args[0][0]
             assert "LIMIT 1000" in executed_sql

             # Verify Audit Log with Retries (for BackgroundTasks)
             import asyncio
             max_retries = 5
             found = False
             async with get_db_connection() as conn:
                 for _ in range(max_retries):
                     async with conn.cursor() as cursor:
                         await cursor.execute("SELECT count(*) FROM sys_api_audit_log WHERE user_id = %s", (setup_permission,))
                         row = await cursor.fetchone()
                         if row[0] >= 1:
                             found = True
                             break
                     await asyncio.sleep(0.5) # Wait for background task
             
             if not found:
                 pytest.fail("Audit log verification failed: No logs found after retries")
