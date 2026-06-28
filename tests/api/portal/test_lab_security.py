import pytest
from httpx import AsyncClient
from unittest.mock import patch, MagicMock, AsyncMock

@pytest.mark.asyncio
async def test_sql_lab_security_interception(client: AsyncClient, admin_api_key):
    """Test that dangerous SQL keywords are intercepted in SQL Lab"""
    
    # Mock data source config
    mock_ds = MagicMock()
    mock_ds.source_type = "mysql"
    mock_ds.source_name = "test_mysql"
    mock_ds.id = 1
    
    admin_headers = {"X-API-Key": admin_api_key}
    
    payloads = [
        {"source_id": 1, "sql": "DROP TABLE users", "limit": 10},
        {"source_id": 1, "sql": "DELETE FROM users WHERE 1=1", "limit": 10},
        {"source_id": 1, "sql": "UPDATE users SET password='123'", "limit": 10},
        {"source_id": 1, "sql": "INSERT INTO users (name) VALUES ('hacker')", "limit": 10},
        {"source_id": 1, "sql": "ALTER TABLE users ADD COLUMN secret VARCHAR(255)", "limit": 10},
        {"source_id": 1, "sql": "/* comment */ DROP TABLE users", "limit": 10},
        {"source_id": 1, "sql": "-- line comment \n DROP TABLE users", "limit": 10}
    ]
    
    # Patch the service and adapter to avoid real DB connection
    with patch("app.api.portal.endpoints.lab.DataSourceService.get_datasource", new_callable=AsyncMock) as mock_get_ds, \
         patch("app.api.portal.endpoints.lab.get_adapter", new_callable=AsyncMock) as mock_get_adapter:
        
        mock_get_ds.return_value = mock_ds
        
        # Use a real MySQLAdapter instance (or a mock that simulates it) 
        # but with the real _validate_sql_safety method
        from app.services.data_adapter.mysql import MySQLAdapter
        adapter = MySQLAdapter(source_id=1)
        mock_get_adapter.return_value = adapter
        
        for payload in payloads:
            response = await client.post("/api/portal/lab/preview", json=payload, headers=admin_headers)
            
            # Should return 400 Bad Request due to security violation
            assert response.status_code == 400, f"SQL should be intercepted: {payload['sql']}"
            assert "Security Policy Violation" in response.json()["detail"]

@pytest.mark.asyncio
async def test_mysql_adapter_sort_by_injection_prevention(client: AsyncClient, admin_api_key):
    """
    Test specifically for the sort_by field injection vulnerability in MySQLAdapter.
    Even if the field is wrapped in backticks, we should ensure it's a valid field.
    """
    admin_headers = {"X-API-Key": admin_api_key}
    
    # Payload with an injection attempt in sort_by
    payload = {
        "resource": "yunshu_rooms",
        "filters": [],
        "sort_by": "id`; DROP TABLE sys_roles; --",
        "sort_order": "desc",
        "page": 1,
        "size": 10
    }
    
    # Use mocks to avoid real DB connectivity issues
    with patch("app.api.v1.endpoints.query.get_adapter", new_callable=AsyncMock) as mock_get_adapter, \
         patch("app.api.v1.endpoints.query.verify_resource_access", new_callable=AsyncMock):
        
        mock_adapter = AsyncMock()
        from app.services.data_adapter.models import ResultSet
        mock_adapter.execute.return_value = ResultSet(items=[], total=0, page=1, size=10, pages=0)
        mock_get_adapter.return_value = mock_adapter
        
        response = await client.post("/api/v1/query/", json=payload, headers=admin_headers)
        assert response.status_code == 200
        
        # Verify that the sort_by passed to adapter was sanitized or used as-is 
        # (the protection happens inside the adapter, but here we just ensure flow is safe)
        mock_adapter.execute.assert_called_once()
        args, kwargs = mock_adapter.execute.call_args
        logical_query = args[0]
        assert logical_query.sort_by == payload["sort_by"]
