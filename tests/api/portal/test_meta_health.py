import pytest
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock

@pytest.mark.asyncio
async def test_trigger_health_check(client: AsyncClient, admin_api_key):
    """测试手动触发健康检查接口"""
    headers = {"X-API-Key": admin_api_key}
    
    # Mock Service
    with patch("app.services.meta_health_service.MetaHealthService.calculate_dataset_health", new_callable=AsyncMock) as mock_health:
        mock_health.return_value = {
            "score": 85,
            "report": {"issues": [], "stats": {"tables": 1}}
        }
        
        response = await client.post("/api/portal/meta/v2/datasets/1/health-check", headers=headers)
        
        assert response.status_code == 200
        assert response.json()["score"] == 85
        mock_health.assert_called_once_with(1)

@pytest.mark.asyncio
async def test_ai_enrich_metadata(client: AsyncClient, admin_api_key):
    """测试 AI 批量润色接口"""
    headers = {"X-API-Key": admin_api_key}
    
    with patch("app.services.metadata_v2_service.MetadataV2Service.batch_enrich_dataset", new_callable=AsyncMock) as mock_enrich:
        response = await client.post("/api/portal/meta/v2/datasets/1/ai-enrich", headers=headers)
        
        assert response.status_code == 200
        assert "completed" in response.json()["message"]
        mock_enrich.assert_called_once_with(1)

@pytest.mark.asyncio
async def test_dataset_detail_contains_health_info(client: AsyncClient, admin_api_key):
    """验证获取数据集详情时包含健康分和报告"""
    headers = {"X-API-Key": admin_api_key}
    
    mock_dataset = {
        "id": 1,
        "name": "test_ds",
        "display_name": "Test Dataset",
        "health_score": 75,
        "health_report": {"issues": [{"msg": "Missing terms"}]},
        "tags": [],
        "data_source": "default",
        "status": 1,
        "tables": [],
        "metrics": [],
        "relationships": []
    }
    
    with patch("app.services.metadata_v2_service.MetadataV2Service.get_dataset_by_id", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_dataset
        
        response = await client.get("/api/portal/meta/v2/datasets/1", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["health_score"] == 75
        assert data["health_report"]["issues"][0]["msg"] == "Missing terms"
