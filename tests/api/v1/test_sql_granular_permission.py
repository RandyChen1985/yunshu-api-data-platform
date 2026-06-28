import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from app.core.database import get_db_connection
from app.services.permission_service import PermissionService

@pytest.fixture
async def test_user(valid_api_key):
    async with get_db_connection() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("SELECT id FROM api_users WHERE user_name = 'test_user'")
            row = await cursor.fetchone()
            user_id = row[0]
            
            # 清理旧权限
            await cursor.execute("DELETE FROM sys_user_resources WHERE user_id = %s", (user_id,))
            await cursor.execute("DELETE FROM sys_ui_permissions WHERE user_id = %s", (user_id,))
            
            # 授权基础权限
            await cursor.execute(
                "INSERT INTO sys_ui_permissions (user_id, perm_type, perm_code) VALUES (%s, 'resource', 'system.sql.execute')",
                (user_id,)
            )
            await conn.commit()
            
            # 清理缓存
            await PermissionService.invalidate_user_cache(user_id)
            return user_id

@pytest.mark.asyncio
async def test_sql_ds_permission_denied(client, valid_api_key, test_user):
    """测试没有数据源权限时被拒绝"""
    with patch("app.api.v1.endpoints.sql_execution.DataSourceService.get_datasource", new_callable=AsyncMock) as mock_get_ds, \
         patch("app.api.v1.endpoints.sql_execution.DataSourceService.get_datasource_by_name", new_callable=AsyncMock) as mock_get_ds_name:
        
        mock_ds = MagicMock(id=1, source_name="clickhouse-test")
        mock_get_ds.return_value = mock_ds
        mock_get_ds_name.return_value = mock_ds
    
        resp = await client.post(
            "/api/v1/sql/execute",
            headers={"X-API-Key": valid_api_key},
            json={"data_source": "clickhouse-test", "sql": "SELECT 1"}
        )
        assert resp.status_code == 403
        assert "No access to data source 'clickhouse-test'" in resp.json()["message"]

@pytest.mark.asyncio
async def test_sql_table_permission_empty_denied(client, valid_api_key, test_user):
    """测试拥有数据源权限但未配置表权限（空=拒绝）"""
    async with get_db_connection() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(
                "INSERT INTO sys_ui_permissions (user_id, perm_type, perm_code) VALUES (%s, 'datasource', 'ds:clickhouse-test')",
                (test_user,)
            )
            await conn.commit()
    await PermissionService.invalidate_user_cache(test_user)
    
    with patch("app.api.v1.endpoints.sql_execution.DataSourceService.get_datasource", new_callable=AsyncMock) as mock_get_ds, \
         patch("app.api.v1.endpoints.sql_execution.DataSourceService.get_datasource_by_name", new_callable=AsyncMock) as mock_get_ds_name:
        
        mock_ds = MagicMock(id=1, source_name="clickhouse-test")
        mock_get_ds.return_value = mock_ds
        mock_get_ds_name.return_value = mock_ds
    
        resp = await client.post(
            "/api/v1/sql/execute",
            headers={"X-API-Key": valid_api_key},
            json={"data_source": "clickhouse-test", "sql": "SELECT * FROM my_table"}
        )
        assert resp.status_code == 403
        assert "No tables authorized" in resp.json()["message"]

@pytest.mark.asyncio
async def test_sql_table_permission_whitelist_success(client, valid_api_key, test_user):
    """测试白名单匹配成功"""
    async with get_db_connection() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(
                "INSERT INTO sys_ui_permissions (user_id, perm_type, perm_code) VALUES (%s, 'datasource', 'ds:clickhouse-test')",
                (test_user,)
            )
            await cursor.execute(
                "INSERT INTO sys_ui_permissions (user_id, perm_type, perm_code) VALUES (%s, 'data_table', 'ds:clickhouse-test:table:users')",
                (test_user,)
            )
            await conn.commit()
    await PermissionService.invalidate_user_cache(test_user)

    with patch("app.api.v1.endpoints.sql_execution.DataSourceService.get_datasource", new_callable=AsyncMock) as mock_get_ds, \
         patch("app.api.v1.endpoints.sql_execution.DataSourceService.get_datasource_by_name", new_callable=AsyncMock) as mock_get_ds_name, \
         patch("app.api.v1.endpoints.sql_execution.get_adapter", new_callable=AsyncMock) as mock_get_adapter:
        
        mock_ds = MagicMock(id=1, source_name="clickhouse-test")
        mock_get_ds.return_value = mock_ds
        mock_get_ds_name.return_value = mock_ds
        
        mock_adapter = MagicMock()
        mock_adapter.execute_sql = AsyncMock(return_value={"columns":[], "items":[]})
        mock_get_adapter.return_value = mock_adapter

        # 1. 匹配表名
        resp = await client.post(
            "/api/v1/sql/execute",
            headers={"X-API-Key": valid_api_key},
            json={"data_source": "clickhouse-test", "sql": "SELECT * FROM users"}
        )
        assert resp.status_code == 200

        # 2. 匹配带别名的表名
        resp = await client.post(
            "/api/v1/sql/execute",
            headers={"X-API-Key": valid_api_key},
            json={"data_source": "clickhouse-test", "sql": "SELECT u.id FROM users AS u"}
        )
        assert resp.status_code == 200

@pytest.mark.asyncio
async def test_sql_table_permission_whitelist_denied(client, valid_api_key, test_user):
    """测试白名单不匹配时拒绝"""
    async with get_db_connection() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(
                "INSERT INTO sys_ui_permissions (user_id, perm_type, perm_code) VALUES (%s, 'datasource', 'ds:clickhouse-test')",
                (test_user,)
            )
            await cursor.execute(
                "INSERT INTO sys_ui_permissions (user_id, perm_type, perm_code) VALUES (%s, 'data_table', 'ds:clickhouse-test:table:users')",
                (test_user,)
            )
            await conn.commit()
    await PermissionService.invalidate_user_cache(test_user)

    with patch("app.api.v1.endpoints.sql_execution.DataSourceService.get_datasource", new_callable=AsyncMock) as mock_get_ds, \
         patch("app.api.v1.endpoints.sql_execution.DataSourceService.get_datasource_by_name", new_callable=AsyncMock) as mock_get_ds_name:
        
        mock_ds = MagicMock(id=1, source_name="clickhouse-test")
        mock_get_ds.return_value = mock_ds
        mock_get_ds_name.return_value = mock_ds
        
        resp = await client.post(
            "/api/v1/sql/execute",
            headers={"X-API-Key": valid_api_key},
            json={"data_source": "clickhouse-test", "sql": "SELECT * FROM secret_table"}
        )
        assert resp.status_code == 403
        assert "No access to table 'secret_table'" in resp.json()["message"]

@pytest.mark.asyncio
async def test_sql_table_permission_all_pass(client, valid_api_key, test_user):
    """测试显式通配符 ALL (*)"""
    async with get_db_connection() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(
                "INSERT INTO sys_ui_permissions (user_id, perm_type, perm_code) VALUES (%s, 'datasource', 'ds:clickhouse-test')",
                (test_user,)
            )
            await cursor.execute(
                "INSERT INTO sys_ui_permissions (user_id, perm_type, perm_code) VALUES (%s, 'data_table', 'ds:clickhouse-test:table:*')",
                (test_user,)
            )
            await conn.commit()
    await PermissionService.invalidate_user_cache(test_user)

    with patch("app.api.v1.endpoints.sql_execution.DataSourceService.get_datasource", new_callable=AsyncMock) as mock_get_ds, \
         patch("app.api.v1.endpoints.sql_execution.DataSourceService.get_datasource_by_name", new_callable=AsyncMock) as mock_get_ds_name, \
         patch("app.api.v1.endpoints.sql_execution.get_adapter", new_callable=AsyncMock) as mock_get_adapter:
        
        mock_ds = MagicMock(id=1, source_name="clickhouse-test")
        mock_get_ds.return_value = mock_ds
        mock_get_ds_name.return_value = mock_ds
        
        mock_adapter = MagicMock()
        mock_adapter.execute_sql = AsyncMock(return_value={"columns":[], "items":[]})
        mock_get_adapter.return_value = mock_adapter

        resp = await client.post(
            "/api/v1/sql/execute",
            headers={"X-API-Key": valid_api_key},
            json={"data_source": "clickhouse-test", "sql": "SELECT * FROM anything"}
        )
        assert resp.status_code == 200