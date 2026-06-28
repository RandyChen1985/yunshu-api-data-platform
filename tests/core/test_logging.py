import pytest
from httpx import AsyncClient
from app.core import database

from unittest.mock import patch, AsyncMock

@pytest.mark.asyncio
async def test_access_log_recording(client: AsyncClient, valid_api_key: str):
    """验证请求会被记录到 MySQL api_access_logs 表"""
    
    # Mock ClickHouse execution to avoid 500 error (since we only care about logging here)
    with patch("app.services.data_adapter.clickhouse.ClickHouseAdapter.execute", new_callable=AsyncMock) as mock_execute:
        from app.services.data_adapter.models import ResultSet
        mock_execute.return_value = ResultSet(items=[], total=0, page=1, size=20, pages=0)

        # 1. 发起请求
        # 1. 发起请求
        response = await client.get(
            "/api/v1/resources/test_donghuan_real_metrics?page=1&size=1",
            headers={"X-API-Key": valid_api_key}
        )
    assert response.status_code == 200
    
    # 验证响应头中包含 X-Trace-Id
    assert "X-Trace-Id" in response.headers
    trace_id = response.headers["X-Trace-Id"]
    
    # 2. 验证数据库 (Wait a bit for async insert)
    import asyncio
    await asyncio.sleep(0.5) 
    
    from app.utils.sharding import get_audit_table_name
    table_name = get_audit_table_name()
    
    async with database.get_db_connection() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(
                f"SELECT id, user_id, status_code, trace_id FROM {table_name} WHERE trace_id = %s",
                (trace_id,)
            )
            row = await cursor.fetchone()
            
            assert row is not None
            assert row[3] == trace_id
            assert row[2] == 200
            # user_id should be present if authenticated
            assert row[1] is not None 

@pytest.mark.asyncio
async def test_access_log_unauthorized(client: AsyncClient):
    """验证未授权请求也会记录（user_id 为空）"""
    response = await client.get("/api/v1/resources/test_donghuan_real_metrics")
    assert response.status_code == 401
    
    trace_id = response.headers.get("X-Trace-Id")
    assert trace_id is not None
    
    # 2. 验证数据库
    import asyncio
    await asyncio.sleep(0.5)
    
    from app.utils.sharding import get_audit_table_name
    table_name = get_audit_table_name()
    
    async with database.get_db_connection() as conn:
        async with conn.cursor() as cursor:
            # Check api_access_logs
            await cursor.execute(
                f"SELECT id, user_id, status_code FROM {table_name} WHERE trace_id = %s",
                (trace_id,)
            )
            row = await cursor.fetchone()
            
            assert row is not None
            assert row[2] == 401
            assert row[1] is None # User ID should be None

@pytest.mark.asyncio
async def test_access_log_with_body(client: AsyncClient, admin_api_key: str):
    """验证 Request Body 和 Response Body 被记录"""
    
    # Pre-requisite: Insert a dummy data source
    async with database.get_db_connection() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("""
                INSERT IGNORE INTO sys_data_source 
                (source_name, source_type, host, port, database_name, username, password, status)
                VALUES ('default', 'clickhouse', 'localhost', 9000, 'default', 'default', '', 1)
            """)
            await conn.commit()
    
            # Mock ClickHouse execution
            with patch("app.services.data_adapter.clickhouse.ClickHouseAdapter.execute_sql", new_callable=AsyncMock) as mock_execute_sql:
                mock_execute_sql.return_value = {
                    "columns": [{"name": "col1", "type": "String"}],
                    "items": [["val1"]]
                }
        
                payload = {"sql": "SELECT 1", "data_source": "default"}
        
                # 1. 发起 POST 请求
                response = await client.post(
                    "/api/v1/sql/execute",
                    json=payload,
                    headers={"X-API-Key": admin_api_key}
                )
                assert response.status_code == 200        
        trace_id = response.headers["X-Trace-Id"]
        
        # 2. 验证数据库
        import asyncio
        await asyncio.sleep(0.5)
        
        from app.utils.sharding import get_audit_table_name
        table_name = get_audit_table_name()
        
        async with database.get_db_connection() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    f"SELECT request_params, response_body, error_message FROM {table_name} WHERE trace_id = %s",
                    (trace_id,)
                )
                row = await cursor.fetchone()
                
                assert row is not None
                request_log, response_log, error_log = row
                
                # 验证 Request Body
                assert request_log is not None
                import json
                req_json = json.loads(request_log)
                assert req_json["sql"] == "SELECT 1"
                
                # 验证 Response Body
                assert response_log is not None
                res_json = json.loads(response_log)
                # Response wrapper: {"code": 200, "data": {"columns": ...}}
                assert res_json["code"] == 200
                assert res_json["data"]["items"][0][0] == "val1"
                
                # 验证 Error Message (Should be None for success)
                assert error_log is None
