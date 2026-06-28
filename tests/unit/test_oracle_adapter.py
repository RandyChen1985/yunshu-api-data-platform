import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.data_adapter.oracle import OracleAdapter
from app.services.data_adapter.models import LogicalQuery
from app.schemas.resource import ResourceResponse

@pytest.fixture
def oracle_adapter():
    return OracleAdapter(source_id=999)

@pytest.fixture
def mock_resource_config():
    return ResourceResponse(
        id=1,
        resource_key="test_oracle",
        resource_name="Test Oracle",
        resource_group="Test",
        data_source="oracle_ds",
        resource_mode="TABLE",
        table_name="USERS",
        fields_config=[
            {"name": "ID", "label": "ID", "type": "Long"}, 
            {"name": "NAME", "label": "Name", "type": "String"}
        ],
        allowed_filters=[{"name": "ID", "label": "ID", "type": "Long"}],
        default_sort="ID",
        status=1,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        cache_ttl=0,
        reference_count=0
    )

class MockCursor:
    def __init__(self):
        self.execute = AsyncMock()
        self.fetchone = AsyncMock()
        self.fetchall = AsyncMock()
        self.description = [("ID",), ("NAME",)]
    async def __aenter__(self): return self
    async def __aexit__(self, *args): pass

class MockConn:
    def __init__(self):
        self._cursor = MockCursor()
        self.cursor = MagicMock(return_value=self._cursor)
        # Compatibility with old tests
        self.cursor_async = MagicMock(return_value=self._cursor)
    async def __aenter__(self): return self
    async def __aexit__(self, *args): pass

@pytest.mark.asyncio
async def test_oracle_execute_basic(oracle_adapter, mock_resource_config):
    """验证 Oracle 基本执行逻辑和分页语法 (11g 兼容)"""
    
    mock_conn = MockConn()
    mock_cursor = mock_conn.cursor()
    
    # 因为 _run_query_internal 会被调用两次且都用 fetchall
    # 第一次是 COUNT(*)，第二次是数据
    mock_cursor.fetchall.side_effect = [
        [(100,)], # Count result
        [(1, "Alice"), (2, "Bob")] # Data result
    ]

    mock_pool = MagicMock()
    mock_pool.acquire = AsyncMock(return_value=mock_conn)

    query = LogicalQuery(
        resource="test_oracle",
        page=1,
        size=20,
        filters=[("ID", "=", 1)],
        sort_by="ID",
        sort_order="ASC"
    )

    with patch('app.services.meta_service.MetaService.get_config', return_value=mock_resource_config), \
         patch('app.services.pool_manager.DataSourcePoolManager.get_pool', return_value=mock_pool):
        
        result = await oracle_adapter.execute(query)
        
        assert result.total == 100
        # 验证 11g 兼容的分页语法
        assert "ROWNUM" in result.generated_sql
        assert "WHERE ROWNUM <=" in result.generated_sql
        assert "\"ID\" ASC" in result.generated_sql
        assert result.items[0]["NAME"] == "Alice"

@pytest.mark.asyncio
async def test_oracle_get_tables(oracle_adapter):
    """验证获取表列表逻辑 (包含视图)"""
    mock_conn = MockConn()
    mock_cursor = mock_conn.cursor()
    # Mock data for Tables and Views
    mock_cursor.fetchall.return_value = [("TABLE1", "TABLE"), ("VIEW1", "VIEW")]

    mock_pool = MagicMock()
    mock_pool.acquire = AsyncMock(return_value=mock_conn)

    with patch('app.services.pool_manager.DataSourcePoolManager.get_pool', return_value=mock_pool):
        tables = await oracle_adapter.get_tables()
        assert len(tables) == 2
        assert tables[0] == {"name": "TABLE1", "type": "TABLE"}
        assert tables[1] == {"name": "VIEW1", "type": "VIEW"}
