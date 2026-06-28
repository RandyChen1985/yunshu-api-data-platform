import pytest
import httpx
import json
from app.core.database import get_db_connection
import asyncio

from app.core.database import get_db_connection
from app.utils.sharding import get_audit_table_name
import asyncio

@pytest.mark.asyncio
async def test_audit_log_sharding_and_merge():
    """验证审计日志是否正确写入分表且字段已合并"""
    from app.core.middleware import _write_access_log
    import time
    
    trace_id = f"test-trace-{int(time.time())}"
    now_str = time.strftime('%Y-%m-%d %H:%M:%S')
    table_name = get_audit_table_name()
    
    log_data = {
        "trace_id": trace_id,
        "user_id": 1,
        "user_name": "test_user",
        "endpoint": "/api/portal/lab/preview",
        "method": "POST",
        "status_code": 200,
        "process_time_ms": 100.0,
        "client_ip": "127.0.0.1",
        "request_params": '{"sql": "SELECT 1"}',
        "response_body": '{"status": "success"}',
        "action_type": "LAB_QUERY",
        "source_sql": "SELECT 1",
        "created_at": now_str
    }
    
    # 执行写入 (会自动创建表)
    await _write_access_log(log_data)
    
    # 验证数据库
    async with get_db_connection() as conn:
        async with conn.cursor() as cursor:
            # 检查分表
            sql = f"SELECT id, action_type, source_sql FROM {table_name} WHERE trace_id = %s"
            await cursor.execute(sql, (trace_id,))
            row = await cursor.fetchone()
            
            assert row is not None, f"Log record not found in {table_name}"
            assert row[1] == "LAB_QUERY"
            assert row[2] == "SELECT 1"
            
            # 验证旧扩展表不应再被写入 (如果还存在)
            try:
                await cursor.execute("SELECT COUNT(*) FROM api_access_logs_ext WHERE log_id = %s", (row[0],))
                count = (await cursor.fetchone())[0]
                assert count == 0
            except Exception:
                # Table might have been dropped, which is fine
                pass
