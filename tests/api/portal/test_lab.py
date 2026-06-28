import pytest
from httpx import AsyncClient
import pytest_asyncio
from app.services.meta_service import MetaService
import time as import_time

# Mock data for testing
# Use a simple MySQL query that works on metadata tables
MOCK_SQL_QUERY = "SELECT * FROM api_users LIMIT 5"
MOCK_PARAMS = {"limit": 5}

async def get_working_datasource_id(client, headers):
    """Helper to find a MySQL datasource that is likely to work"""
    response = await client.get("/api/portal/datasource/datasources", headers=headers)
    datasources = response.json()
    # Prefer 'api_data' (MySQL) as it points to the app's own DB which is guaranteed to be up in tests
    for ds in datasources:
        if ds['source_type'] == 'mysql':
            return ds['id']
    
    # Fallback to first one if no MySQL found (though conftest should create one?)
    # Actually conftest creates 'default_clickhouse'. We should probably let conftest create a mysql one too.
    if datasources:
        return datasources[0]['id']
    return None

@pytest.fixture
def admin_auth_headers(admin_api_key):
    return {"X-API-Key": admin_api_key}

@pytest.mark.asyncio
async def test_preview_sql_success(client: AsyncClient, admin_auth_headers):
    """Test successful SQL preview execution"""
    source_id = await get_working_datasource_id(client, admin_auth_headers)
    if not source_id:
        pytest.skip("No suitable datasource found")

    payload = {
        "source_id": source_id,
        "sql": MOCK_SQL_QUERY,
        "limit": 10
    }
    
    response = await client.post("/api/portal/lab/preview", json=payload, headers=admin_auth_headers)
    
    # If 500, check if it's a connection error and skip if so (useful for CI environments)
    if response.status_code == 500:
        error_msg = (response.json().get("detail", "") or response.json().get("message", "")).lower()
        skip_keywords = ["connection refused", "connectionrefused", "timeout", "network is unreachable", "failed to connect", "retryerror"]
        if any(kw in error_msg for kw in skip_keywords):
            pytest.skip(f"Datasource connection failed: {error_msg}")
        print(f"Error response: {response.text}")
        
    assert response.status_code == 200
    data = response.json()
    
    assert "columns" in data
    assert "rows" in data
    assert "execution_time_ms" in data
    assert len(data["rows"]) <= 10

@pytest.mark.asyncio
async def test_preview_sql_with_params(client: AsyncClient, admin_auth_headers):
    """Test SQL preview with Jinja2 parameters"""
    source_id = await get_working_datasource_id(client, admin_auth_headers)
    if not source_id: pytest.skip("No datasource")

    # Test with a parameter (MySQL syntax for app DB)
    sql_with_param = "SELECT * FROM api_users WHERE user_name = {{ name }}"
    params = {"name": "'test_admin'"} 
    
    payload = {
        "source_id": source_id,
        "sql": sql_with_param,
        "params": params,
        "limit": 10
    }
    
    response = await client.post("/api/portal/lab/preview", json=payload, headers=admin_auth_headers)
    assert response.status_code == 200
    data = response.json()
    # Should find test_admin
    assert len(data["rows"]) >= 1 

@pytest.mark.asyncio
async def test_preview_sql_dangerous_keyword(client: AsyncClient, admin_auth_headers):
    """Test that dangerous SQL keywords are blocked"""
    source_id = await get_working_datasource_id(client, admin_auth_headers)
    if not source_id: pytest.skip("No datasource")

    payload = {
        "source_id": source_id,
        "sql": "DROP TABLE api_users", # Dangerous!
        "limit": 10
    }
    
    response = await client.post("/api/portal/lab/preview", json=payload, headers=admin_auth_headers)
    assert response.status_code == 400
    # The global exception handler puts the exception detail into the 'message' field
    # and sets 'detail' to None.
    message = response.json()["message"]
    assert "Security Policy Violation" in str(message)


@pytest.mark.asyncio
async def test_publish_api_success(client: AsyncClient, admin_auth_headers):
    """Test publishing an API from SQL Lab"""
    # 1. Prepare resource data
    resource_key = f"test.lab.api.{int(import_time.time())}"
    
    payload = {
        "resource_key": resource_key,
        "resource_name": "Test Lab API",
        "resource_group": "TEST",
        "data_source": "default", # Assuming 'default' exists name, might need to fetch name
        "resource_mode": "SQL",
        "table_name": None,
        "custom_sql": "SELECT 1",
        "fields_config": [{"name": "1", "label": "One", "type": "UInt8"}],
        "allowed_filters": [],
        "default_sort": "",
        "status": 1,
        "cache_ttl": 60
    }
    
    # Need to make sure we clean up if it exists or use random key
    # Using random key strategy above
    
    response = await client.post("/api/portal/lab/publish", json=payload, headers=admin_auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["resource_key"] == resource_key
    
    # Clean up
    await MetaService.delete_resource(resource_key)

@pytest.mark.asyncio
async def test_clickhouse_connectivity(client: AsyncClient, admin_auth_headers):
    """Test ClickHouse connectivity if available"""
    response = await client.get("/api/portal/datasource/datasources", headers=admin_auth_headers)
    datasources = response.json()
    
    ck_source = next((ds for ds in datasources if ds['source_type'] == 'clickhouse'), None)
    if not ck_source:
        pytest.skip("No ClickHouse datasource found")

    payload = {
        "source_id": ck_source['id'],
        "sql": "SELECT 1",
        "limit": 1
    }
    
    response = await client.post("/api/portal/lab/preview", json=payload, headers=admin_auth_headers)
    
    # 针对 GitLab CI 等没有真实 CK 环境的情况，捕获连接失败并跳过
    if response.status_code == 500:
        error_msg = response.json().get("detail", "") or response.json().get("message", "")
        # 转换为小写并匹配更多可能的错误标识
        err_lower = error_msg.lower()
        skip_keywords = [
            "connection refused", "connectionrefused", "timeout",
            "network is unreachable", "failed to connect", "can't connect",
            "retryerror", "connection reset", "authentication failed"
        ]
        if any(kw in err_lower for kw in skip_keywords):
            pytest.skip(f"ClickHouse connection failed: {error_msg}. Skipping.")
    if response.status_code == 400:
        error_msg = response.json().get("detail", "") or response.json().get("message", "")
        if "Authentication failed" in error_msg or "Connect call failed" in error_msg:
            pytest.skip(f"ClickHouse connection/auth failed (400): {error_msg}. Skipping.")
        
    assert response.status_code == 200
    data = response.json()
    assert len(data["rows"]) == 1
    assert data["rows"][0][0] == 1