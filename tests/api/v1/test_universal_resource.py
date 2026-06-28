import pytest
from httpx import AsyncClient
from unittest.mock import patch, MagicMock, AsyncMock
from dataclasses import dataclass, field
from typing import List, Any

@dataclass
class MockResultSet:
    items: List[Any] = field(default_factory=list)
    total: int = 10
    page: int = 1
    size: int = 20
    pages: int = 1

# Helper to create mock result
def create_mock_result(items=None, total=10, page=1, size=20):
    if items is None:
        items = [{"id": 1, "name": "Item 1"}]
    return MockResultSet(items=items, total=total, page=page, size=size, pages=(total + size - 1) // size)

@pytest.mark.asyncio
async def test_get_resource_success(client: AsyncClient, valid_api_key: str):
    """测试常规动态资源获取"""
    with patch("app.services.meta_service.MetaService.get_config", new_callable=AsyncMock) as mock_get_config, \
         patch("app.api.v1.endpoints.universal.get_adapter", new_callable=AsyncMock) as mock_get_adapter, \
         patch("app.api.v1.endpoints.universal.verify_resource_access", new_callable=AsyncMock):
        
        mock_config = MagicMock()
        mock_config.data_source = "mock_ds"
        mock_get_config.return_value = mock_config

        mock_adapter = AsyncMock()
        mock_adapter.execute.return_value = create_mock_result()
        mock_get_adapter.return_value = mock_adapter

        response = await client.get(
            "/api/v1/resources/donghuan_real_metrics",
            headers={"X-API-Key": valid_api_key}
        )
        
        assert response.status_code == 200
        json_data = response.json()
        assert json_data["code"] == 200
        assert "data" in json_data

@pytest.mark.asyncio
async def test_get_resource_pagination(client: AsyncClient, valid_api_key: str):
    """测试分页参数"""
    with patch("app.services.meta_service.MetaService.get_config", new_callable=AsyncMock) as mock_get_config, \
         patch("app.api.v1.endpoints.universal.get_adapter", new_callable=AsyncMock) as mock_get_adapter, \
         patch("app.api.v1.endpoints.universal.verify_resource_access", new_callable=AsyncMock):

        mock_config = MagicMock()
        mock_config.data_source = "mock_ds"
        mock_get_config.return_value = mock_config

        mock_adapter = AsyncMock()
        mock_adapter.execute.return_value = create_mock_result(page=1, size=10)
        mock_get_adapter.return_value = mock_adapter

        response = await client.get(
            "/api/v1/resources/yunshu_rooms",
            params={"page": 1, "size": 10},
            headers={"X-API-Key": valid_api_key}
        )
        
        assert response.status_code == 200
        data = response.json()["data"]
        assert data.get("page") == 1
        assert data.get("size") == 10

@pytest.mark.asyncio
async def test_get_resource_filtering(client: AsyncClient, valid_api_key: str):
    """测试资源过滤"""
    with patch("app.services.meta_service.MetaService.get_config", new_callable=AsyncMock) as mock_get_config, \
         patch("app.api.v1.endpoints.universal.get_adapter", new_callable=AsyncMock) as mock_get_adapter, \
         patch("app.api.v1.endpoints.universal.verify_resource_access", new_callable=AsyncMock):
        
        mock_get_config.return_value.data_source = "mock_ds"
        mock_get_adapter.return_value.execute.return_value = create_mock_result()

        response = await client.get(
            "/api/v1/resources/yunshu_rooms",
            params={"jfbm": "RO-BJ-01"},
            headers={"X-API-Key": valid_api_key}
        )
        
        assert response.status_code == 200

@pytest.mark.asyncio
async def test_get_resource_sorting(client: AsyncClient, valid_api_key: str):
    """测试排序参数"""
    with patch("app.services.meta_service.MetaService.get_config", new_callable=AsyncMock) as mock_get_config, \
         patch("app.api.v1.endpoints.universal.get_adapter", new_callable=AsyncMock) as mock_get_adapter, \
         patch("app.api.v1.endpoints.universal.verify_resource_access", new_callable=AsyncMock):
        
        mock_get_config.return_value.data_source = "mock_ds"
        mock_get_adapter.return_value.execute.return_value = create_mock_result()

        response = await client.get(
            "/api/v1/resources/donghuan_events",
            params={"sort_by": "rowkey", "sort_order": "ASC"},
            headers={"X-API-Key": valid_api_key}
        )
        
        assert response.status_code == 200

@pytest.mark.asyncio
async def test_get_non_existent_resource(client: AsyncClient, admin_api_key: str):
    """Test accessing non-existent resource"""
    response = await client.get(
        "/api/v1/resources/non_existent_resource",
        headers={"X-API-Key": admin_api_key}
    )
    # 400 Bad Request is returned for unknown resources (validation)
    assert response.status_code == 400

@pytest.mark.asyncio
async def test_get_resource_invalid_filter(client: AsyncClient, valid_api_key: str):
    """测试使用不允许的过滤器"""
    with patch("app.services.meta_service.MetaService.get_config", new_callable=AsyncMock) as mock_get_config, \
         patch("app.api.v1.endpoints.universal.get_adapter", new_callable=AsyncMock) as mock_get_adapter, \
         patch("app.api.v1.endpoints.universal.verify_resource_access", new_callable=AsyncMock):
        
        mock_get_config.return_value.data_source = "mock_ds"
        mock_get_adapter.return_value.execute.return_value = create_mock_result()

        response = await client.get(
            "/api/v1/resources/yunshu_rooms",
            params={"random_field": "some_value"},
            headers={"X-API-Key": valid_api_key}
        )
        
        assert response.status_code == 200

@pytest.mark.asyncio
async def test_get_resource_unauthorized(client: AsyncClient):
    """测试未授权访问"""
    response = await client.get("/api/v1/resources/yunshu_rooms")
    assert response.status_code == 401
