import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from typing import AsyncGenerator

@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Async client for testing FastAPI app with explicit lifespan management for tests"""
    from app.core import database, redis
    from app.core.database import get_db_connection
    from app.core.redis import get_redis
    from app.utils.encryption import get_api_key_manager
    import json
    
    # Manually trigger startup
    await database.init_db()
    # await database.init_clickhouse()
    await redis.init_redis()
    
    # Clear Redis cache to ensure permissions are fresh
    r = await get_redis()
    if r:
        await r.flushdb()
    
    # 获取加密管理器来计算测试 Key 的哈希
    manager = get_api_key_manager()
    # Change keys to avoid collision with old admin/demo_user if they persist
    admin_key = "TestAdmin_4wMogHLKDhTDmdwaYFs2ubNDVLXq6Fp4egn0uQ"
    user_key = "TestUser_yf4wflfNQiggz3HD2Px5o2dJEVl6rcgLoiDJa8I"
    
    admin_hash = manager.hash_api_key(admin_key)
    user_hash = manager.hash_api_key(user_key)
    
    admin_encrypted = manager.encrypt_api_key(admin_key)
    user_encrypted = manager.encrypt_api_key(user_key)
    
    # Grant full permissions to demo_user for testing
    all_resources = [
        "test_donghuan_real_metrics", "test_donghuan_events", 
        "test_yunshu_rooms", "test_yunshu_racks", "test_yunshu_device_points",
        "test_ccg_resources", "test_ccg_virtual_machines", "test_ccg_containers"
    ]
    perms_json = json.dumps({"allowed_resources": all_resources})
    admin_perms = json.dumps({"access": ["all"]})
    
    # Map of resource key to table name for testing
    resource_table_map = {
        "test_donghuan_real_metrics": "ck_fact_donghuan_real_metric_hbase",
        "test_donghuan_events": "ck_fact_donghuan_event_detail_hbase",
        "test_yunshu_rooms": "ck_fact_yunshu_resroom_hbase",
        "test_yunshu_racks": "ck_fact_yunshu_resjj_hbase",
        "test_yunshu_device_points": "ck_fact_yunshu_devicepoint_hbase",
    }
    
    # Specific fields_config for resources to avoid SQL errors (missing columns)
    resource_fields_map = {
        "test_donghuan_real_metrics": [
            {"name": "rowkey", "label": "行键", "type": "String"},
            {"name": "metric_name", "label": "指标", "type": "String"},
            {"name": "metric_value", "label": "值", "type": "String"},
            {"name": "metric_time", "label": "时间", "type": "String"}
        ],
        "test_donghuan_events": [
            {"name": "rowkey", "label": "行键", "type": "String"},
            {"name": "event_id", "label": "事件ID", "type": "String"},
            {"name": "event_message", "label": "内容", "type": "String"},
            {"name": "event_time", "label": "时间", "type": "String"}
        ],
        "test_yunshu_rooms": [
            {"name": "rowkey", "label": "行键", "type": "String"},
            {"name": "jfbm", "label": "编号", "type": "String"},
            {"name": "jfmc", "label": "名称", "type": "String"}
        ],
        "test_yunshu_racks": [
            {"name": "rowkey", "label": "行键", "type": "String"},
            {"name": "jjbm", "label": "编号", "type": "String"}
        ],
        "test_yunshu_device_points": [
            {"name": "rowkey", "label": "行键", "type": "String"},
            {"name": "dwmc", "label": "名称", "type": "String"}
        ]
    }
    
    async with get_db_connection() as conn:
        async with conn.cursor() as cursor:
            # 确保测试环境有所需的数据源
            print("🗄️ Seeding data sources...")
            await cursor.execute("DELETE FROM sys_data_source WHERE source_name IN ('default_clickhouse', 'api_data')")
            
            # 清理审计日志分表数据，使用 DELETE 而非 DROP 以避免元数据锁死锁
            await cursor.execute("SHOW TABLES LIKE 'api_access_logs_20%%'")
            audit_tables = [row[0] for row in await cursor.fetchall()]
            for table in audit_tables:
                await cursor.execute(f"DELETE FROM {table}")
            
            # 清理聚合统计表
            await cursor.execute("DELETE FROM api_access_stats_1m")
            
            # ClickHouse
            await cursor.execute(
                """INSERT INTO sys_data_source 
                   (source_name, source_type, host, port, database_name, username, password, status) 
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                ("default_clickhouse", "clickhouse", "localhost", 9000, "default", "admin", "admin123", 1)
            )
            
            # MySQL (Self)
            await cursor.execute(
                """INSERT INTO sys_data_source 
                   (source_name, source_type, host, port, database_name, username, password, status) 
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                ("api_data", "mysql", "localhost", 3306, "yunshu_api_data_platform", "root", "root123", 1)
            )

            # 确保测试环境有这两个用户
            print("🚀 Seeding test users...")
            await cursor.execute("DELETE FROM api_users WHERE user_name IN ('test_admin', 'test_user')")
            
            # 插入管理员
            await cursor.execute(
                """INSERT INTO api_users (user_name, api_key_hash, api_key_encrypted, role, status) 
                   VALUES (%s, %s, %s, %s, %s)""",
                ("test_admin", admin_hash, admin_encrypted, "admin", 1)
            )
            admin_id = cursor.lastrowid
            
            # 插入普通用户
            await cursor.execute(
                """INSERT INTO api_users (user_name, api_key_hash, api_key_encrypted, role, status) 
                   VALUES (%s, %s, %s, %s, %s)""",
                ("test_user", user_hash, user_encrypted, "user", 1)
            )
            user_id = cursor.lastrowid

            # 插入资源元数据以满足外键约束
            print("📦 Seeding resource metadata...")
            for res_key in all_resources:
                table_name = resource_table_map.get(res_key, "mock_table")
                
                # Use specific fields if available, otherwise generic ones
                fields = resource_fields_map.get(res_key, [
                    {"name": "rowkey", "label": "行键", "type": "String"},
                    {"name": "name", "label": "名称", "type": "String"}
                ])
                fields_config = json.dumps(fields)
                allowed_filters = json.dumps([{"name": f["name"], "label": f["label"], "type": "String"} for f in fields[:2]])
                
                await cursor.execute(
                    """REPLACE INTO sys_resource_meta 
                       (resource_key, resource_name, resource_group, status, table_name, fields_config, allowed_filters) 
                       VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                    (res_key, res_key.replace("_", " ").title(), "Test", 1, table_name, fields_config, allowed_filters)
                )

            # 插入权限映射到新表
            if user_id:
                print(f"🔗 Seeding permissions for test_user (ID: {user_id})...")
                for res_key in all_resources:
                    await cursor.execute(
                        "INSERT IGNORE INTO sys_user_resources (user_id, resource_key) VALUES (%s, %s)",
                        (user_id, res_key)
                    )
            await conn.commit()
    
    async with AsyncClient(
        transport=ASGITransport(app=app), 
        base_url="http://testserver"
    ) as ac:
        yield ac
    
    # Manually trigger shutdown
    await redis.close_redis()
    # await database.close_clickhouse()
    await database.close_db()

@pytest.fixture
def valid_api_key() -> str:
    """Get a valid API Key for testing (demo_user - regular user)"""
    return "TestUser_yf4wflfNQiggz3HD2Px5o2dJEVl6rcgLoiDJa8I"

@pytest.fixture
def admin_api_key() -> str:
    """Get an admin API Key for testing"""
    return "TestAdmin_4wMogHLKDhTDmdwaYFs2ubNDVLXq6Fp4egn0uQ"