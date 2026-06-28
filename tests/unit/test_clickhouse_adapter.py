import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from datetime import datetime
from app.services.data_adapter.clickhouse import ClickHouseAdapter
from app.services.data_adapter.models import LogicalQuery
from app.schemas.resource import ResourceResponse, FieldConfig

@pytest.fixture
def mock_config():
    return ResourceResponse(
        id=1,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        resource_key="test_resource",
        resource_name="Test Resource",
        resource_type="clickhouse",
        resource_mode="TABLE",
        table_name="test_table",
        fields_config=[
            FieldConfig(name="metric_name", label="Metric Name", type="String"),
            FieldConfig(name="metric_value", label="Metric Value", type="String"),
            FieldConfig(name="metric_time", label="Time", type="DateTime")
        ],
        allowed_filters=[
            FieldConfig(name="metric_name", label="Metric Name", type="String"),
            FieldConfig(name="metric_value", label="Metric Value", type="String"),
            FieldConfig(name="metric_time", label="Time", type="DateTime"),
            FieldConfig(name="host", label="Host", type="String")
        ],
        default_sort="metric_time"
    )

@pytest.mark.asyncio
async def test_build_where_parameterization(mock_config):
    adapter = ClickHouseAdapter(source_id=1)
    
    query = LogicalQuery(
        resource="test_resource",
        filters=[
            ("metric_name", "=", "cpu_usage"),
            ("metric_value", ">", "80")
        ]
    )
    
    where_sql, params = adapter._build_where(query, mock_config)
    
    assert "metric_name = {metric_name_0}" in where_sql
    assert "metric_value > {metric_value_1}" in where_sql
    assert params["metric_name_0"] == "cpu_usage"
    assert params["metric_value_1"] == "80"

@pytest.mark.asyncio
async def test_build_where_in_clause(mock_config):
    adapter = ClickHouseAdapter(source_id=1)
    
    query = LogicalQuery(
        resource="test_resource",
        filters=[
            ("host", "IN", ["host1", "host2"])
        ]
    )
    
    where_sql, params = adapter._build_where(query, mock_config)
    
    assert "host IN {host_0}" in where_sql
    assert params["host_0"] == ("host1", "host2")

@pytest.mark.asyncio
async def test_execute_parameterized(mock_config):
    adapter = ClickHouseAdapter(source_id=1)
    
    with patch("app.services.meta_service.MetaService.get_config", new_callable=AsyncMock) as mock_get_config:
        mock_get_config.return_value = mock_config
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        
        mock_cursor_obj = AsyncMock()
        mock_cursor_obj.execute = AsyncMock()
        mock_cursor_obj.fetchone = AsyncMock(return_value=(100,))
        mock_cursor_obj.fetchall = AsyncMock(return_value=[("cpu_usage", "90", "2023-01-01 12:00:00")])
        
        mock_cursor.__aenter__.return_value = mock_cursor_obj
        mock_cursor.__aexit__.return_value = None
        
        mock_conn.cursor.return_value = mock_cursor
        
        mock_conn_ctx = MagicMock()
        mock_conn_ctx.__aenter__.return_value = mock_conn
        mock_conn_ctx.__aexit__.return_value = None
        
        with patch("app.services.pool_manager.DataSourcePoolManager.get_pool") as mock_get_pool:
            mock_pool = MagicMock()
            mock_pool.connection.return_value = mock_conn_ctx
            mock_get_pool.return_value = mock_pool

            query = LogicalQuery(resource="test_resource",
                filters=[("metric_name", "=", "cpu_usage")],
                page=1,
                size=10
            )
            
            result = await adapter.execute(query)
            
            assert mock_cursor_obj.execute.call_count == 2
            call_args_list = mock_cursor_obj.execute.call_args_list
            count_call = call_args_list[0]
            select_call = call_args_list[1]
            
            assert "SELECT COUNT(*) FROM test_table" in count_call[0][0]
            assert "SELECT metric_name, metric_value, metric_time" in select_call[0][0]

@pytest.mark.asyncio
async def test_clickhouse_get_tables():
    """验证 ClickHouse 获取表列表逻辑 (修正 system.tables 查询)"""
    adapter = ClickHouseAdapter(source_id=1)
    
    mock_rows = [
        ("table1", "MergeTree"),
        ("view1", "View"),
        ("mv1", "MaterializedView")
    ]
    
    mock_cursor_obj = AsyncMock()
    mock_cursor_obj.fetchall = AsyncMock(return_value=mock_rows)
    mock_cursor_obj.execute = AsyncMock()
    
    mock_cursor = MagicMock()
    mock_cursor.__aenter__ = AsyncMock(return_value=mock_cursor_obj)
    mock_cursor.__aexit__ = AsyncMock()
    
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    
    mock_conn_ctx = MagicMock()
    mock_conn_ctx.__aenter__ = AsyncMock(return_value=mock_conn)
    mock_conn_ctx.__aexit__ = AsyncMock()
    
    with patch("app.services.pool_manager.DataSourcePoolManager.get_pool") as mock_get_pool:
        mock_pool = MagicMock()
        mock_pool.connection.return_value = mock_conn_ctx
        mock_get_pool.return_value = mock_pool
        
        tables = await adapter.get_tables()
        
        assert len(tables) == 3
        assert tables[0] == {"name": "table1", "type": "TABLE"}
        assert tables[1] == {"name": "view1", "type": "VIEW"}
        assert tables[2] == {"name": "mv1", "type": "VIEW"}
        
        args, _ = mock_cursor_obj.execute.call_args
        assert "FROM system.tables" in args[0]
        assert "currentDatabase()" in args[0]
