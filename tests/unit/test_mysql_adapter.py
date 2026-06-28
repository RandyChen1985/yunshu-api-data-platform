import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from app.services.data_adapter.mysql import MySQLAdapter
from app.services.data_adapter.models import LogicalQuery
from app.schemas.resource import ResourceResponse, FieldConfig
from pydantic import ValidationError

@pytest.fixture
def mock_config():
    from datetime import datetime
    return ResourceResponse(
        id=1,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        resource_key="test_resource",
        resource_name="Test",
        resource_group="TestGroup",
        resource_mode="TABLE",
        table_name="test_table",
        fields_config=[
            FieldConfig(name="id", type="INT", label="ID"),
            FieldConfig(name="name", type="VARCHAR", label="Name")
        ],
        allowed_filters=[FieldConfig(name="id", type="INT", label="ID")],
        default_sort="id",
        status=1
    )

@pytest.mark.asyncio
async def test_mysql_adapter_sort_by_protection(mock_config):
    """Test that MySQLAdapter protects against sort_by injection by falling back to default_sort"""
    adapter = MySQLAdapter(source_id=1)
    
    # 1. Valid sort_by
    query_valid = LogicalQuery(resource="test_resource", sort_by="name", sort_order="asc")
    
    # 2. Malicious sort_by (Injection attempt)
    query_malicious = LogicalQuery(resource="test_resource", sort_by="id`; DROP TABLE users; --", sort_order="desc")
    
    with patch("app.services.meta_service.MetaService.get_config", new_callable=AsyncMock) as mock_get_config, \
         patch("app.services.pool_manager.DataSourcePoolManager.get_pool", new_callable=AsyncMock) as mock_get_pool:
        
        mock_get_config.return_value = mock_config
        
        # Mock pool and cursor
        mock_cursor = AsyncMock()
        mock_cursor.fetchall.return_value = []
        
        # Connection Mock
        mock_conn = MagicMock()
        # Mock cursor() call to return a context manager
        mock_cursor_cm = MagicMock()
        mock_cursor_cm.__aenter__ = AsyncMock(return_value=mock_cursor)
        mock_cursor_cm.__aexit__ = AsyncMock()
        mock_conn.cursor.return_value = mock_cursor_cm
        
        # Pool Mock
        mock_pool = MagicMock()
        # Mock acquire() call to return a context manager
        mock_conn_cm = MagicMock()
        mock_conn_cm.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_conn_cm.__aexit__ = AsyncMock()
        mock_pool.acquire.return_value = mock_conn_cm
        
        mock_get_pool.return_value = mock_pool
        
        # Execute valid query
        await adapter.execute(query_valid)
        args, _ = mock_cursor.execute.call_args
        executed_sql = args[0]
        assert "ORDER BY `name` ASC" in executed_sql
        
        # Execute malicious query
        await adapter.execute(query_malicious)
        args, _ = mock_cursor.execute.call_args
        executed_sql = args[0]
        # Should have fallen back to default_sort "id" instead of using the malicious string
        assert "ORDER BY `id` DESC" in executed_sql
        assert "DROP TABLE" not in executed_sql

@pytest.mark.asyncio
async def test_mysql_get_tables():
    """验证 MySQL 获取表列表逻辑 (包含视图类型识别)"""
    adapter = MySQLAdapter(source_id=1)
    
    # Mock data for SHOW FULL TABLES
    # Row format: (Table_name, Table_type)
    mock_rows = [
        ("table1", "BASE TABLE"),
        ("view1", "VIEW"),
        ("sys_view", "SYSTEM VIEW")
    ]
    
    with patch("app.services.pool_manager.DataSourcePoolManager.get_pool", new_callable=AsyncMock) as mock_get_pool:
        # Mock pool and cursor
        mock_cursor = AsyncMock()
        mock_cursor.fetchall.return_value = mock_rows
        
        mock_conn = MagicMock()
        mock_cursor_cm = MagicMock()
        mock_cursor_cm.__aenter__ = AsyncMock(return_value=mock_cursor)
        mock_conn.cursor.return_value = mock_cursor_cm
        
        mock_pool = MagicMock()
        mock_conn_cm = MagicMock()
        mock_conn_cm.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_pool.acquire.return_value = mock_conn_cm
        
        mock_get_pool.return_value = mock_pool
        
        tables = await adapter.get_tables()
        
        assert len(tables) == 3
        assert tables[0] == {"name": "table1", "type": "TABLE"}
        assert tables[1] == {"name": "view1", "type": "VIEW"}
        assert tables[2] == {"name": "sys_view", "type": "VIEW"}
        
        # Verify SQL
        args, _ = mock_cursor.execute.call_args
        assert args[0].upper() == "SHOW FULL TABLES"
