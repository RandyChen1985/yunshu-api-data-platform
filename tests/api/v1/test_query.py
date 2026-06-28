import pytest
from httpx import AsyncClient
from unittest.mock import patch, MagicMock, AsyncMock

@pytest.mark.asyncio
async def test_generic_query_success(client: AsyncClient, valid_api_key: str):
    """测试通用查询接口: 正常查询流程"""
    payload = {
        "resource": "test_donghuan_real_metrics",
        "filters": [
            ["metric_name", "=", "temperature_rack_inlet"],
            ["metric_value", ">", "20"]
        ],
        "page": 1,
        "size": 10
    }
    
    # Mock result object (ResultSet)
    mock_result = MagicMock()
    mock_result.items = [
        {
            "metric_name": "temperature_rack_inlet", 
            "metric_value": "24.5", 
            "metric_time": "2023-01-01 12:00:00"
        }
    ]
    mock_result.total = 1
    mock_result.page = 1
    mock_result.size = 10
    mock_result.pages = 1

    # Mock adapter instance
    mock_adapter = MagicMock()
    mock_adapter.execute = AsyncMock(return_value=mock_result)
    
    # Patch get_adapter in the endpoints module
    # Since get_adapter is async, we use AsyncMock for the function itself
    with patch("app.api.v1.endpoints.query.get_adapter", new_callable=AsyncMock) as mock_get_adapter_func:
        mock_get_adapter_func.return_value = mock_adapter
        
        response = await client.post(
            "/api/v1/query/",
            json=payload,
            headers={"X-API-Key": valid_api_key}
        )
        
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["code"] == 200
        assert "data" in data
        assert "items" in data["data"]
        # 验证返回的数据结构是否符合 donghuan_real_metrics 的字段
        if len(data["data"]["items"]) > 0:
            item = data["data"]["items"][0]
            assert "metric_name" in item
            assert "metric_value" in item
            assert item["metric_value"] == "24.5"

@pytest.mark.asyncio
async def test_generic_query_invalid_resource(client: AsyncClient, admin_api_key: str):
    """测试通用查询接口: 非法资源名"""
    payload = {
        "resource": "invalid_table_name_injection_attempt",
        "filters": [],
        "page": 1,
        "size": 10
    }
    
    response = await client.post(
        "/api/v1/query/",
        json=payload,
        headers={"X-API-Key": admin_api_key}
    )
    
    # 预期失败 (400 Bad Request defined in query.py)
    assert response.status_code == 400
    assert "Unknown resource" in response.text

@pytest.mark.asyncio
async def test_generic_query_invalid_filters_format(client: AsyncClient, valid_api_key: str):
    """测试通用查询接口: 错误的过滤器格式"""
    payload = {
        "resource": "test_donghuan_real_metrics",
        "filters": [
            ["metric_name", "temperature"] # 缺少操作符
        ],
        "page": 1,
        "size": 10
    }
    
    response = await client.post(
        "/api/v1/query/",
        json=payload,
        headers={"X-API-Key": valid_api_key}
    )
    
    # 预期失败 (400 Bad Request from query.py validation)
    assert response.status_code == 400
    assert "must be a list of 3 elements" in response.text
