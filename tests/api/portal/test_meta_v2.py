import pytest
import json
from unittest.mock import patch, AsyncMock
from app.core.database import get_db_connection

@pytest.fixture(autouse=True)
async def cleanup_meta_datasets():
    """每个测试运行前清理残留数据"""
    async with get_db_connection() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("DELETE FROM meta_datasets WHERE name LIKE 'api_test_%%' OR name LIKE 'yaml_test%%' OR name LIKE 'recommend_test%%'")
            await conn.commit()
    yield

@pytest.mark.asyncio
async def test_get_datasets_api(client, admin_api_key):
    """测试获取数据集列表接口"""
    response = await client.get(
        "/api/portal/meta/v2/datasets",
        headers={"X-API-Key": admin_api_key}
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

@pytest.mark.asyncio
async def test_dataset_full_lifecycle_api(client, admin_api_key):
    """测试数据集 API 的完整生命周期 (创建 -> 详情 -> 更新 -> 删除)"""
    # 1. 创建
    ds_payload = {
        "name": "api_test_ds",
        "display_name": "API Test Dataset",
        "description": "Test Desc",
        "data_source": "api_data",
        "tags": ["api", "test"]
    }
    create_res = await client.post(
        "/api/portal/meta/v2/datasets",
        headers={"X-API-Key": admin_api_key},
        json=ds_payload
    )
    assert create_res.status_code == 200
    ds_id = create_res.json()["id"]

    # 2. 详情
    detail_res = await client.get(
        f"/api/portal/meta/v2/datasets/{ds_id}",
        headers={"X-API-Key": admin_api_key}
    )
    assert detail_res.status_code == 200
    assert detail_res.json()["name"] == "api_test_ds"

    # 3. 更新
    update_res = await client.put(
        f"/api/portal/meta/v2/datasets/{ds_id}",
        headers={"X-API-Key": admin_api_key},
        json={"display_name": "API Updated Name"}
    )
    assert update_res.status_code == 200

    # 4. 删除
    del_res = await client.delete(
        f"/api/portal/meta/v2/datasets/{ds_id}",
        headers={"X-API-Key": admin_api_key}
    )
    assert del_res.status_code == 200

@pytest.mark.asyncio
async def test_analyze_ddl_api(client, admin_api_key):
    """测试 DDL 智能分析接口 (Mock AI Service)"""
    # 使用 patch 代替 mocker
    with patch("app.services.ai_service.AIService.chat_completion", new_callable=AsyncMock) as mock_ai:
        mock_ai.return_value = json.dumps({
            "tables": [{"physical_name": "users", "term": "用户表", "columns": []}],
            "metrics": [],
            "relationships": []
        })
        
        payload = {"content": "CREATE TABLE users (id int);"}
        response = await client.post(
            "/api/portal/meta/v2/datasets/analyze-ddl",
            headers={"X-API-Key": admin_api_key},
            json=payload
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert "tables" in data
        assert data["tables"][0]["physical_name"] == "users"

@pytest.mark.asyncio
async def test_recommend_metrics_api(client, admin_api_key):
    """测试指标推荐接口 (Mock AI)"""
    # 先创建一个数据集
    create_res = await client.post(
        "/api/portal/meta/v2/datasets",
        headers={"X-API-Key": admin_api_key},
        json={"name": "recommend_test", "data_source": "api_data"}
    )
    ds_id = create_res.json()["id"]

    try:
        # Mock AI 响应
        with patch("app.services.ai_service.AIService.chat_completion", new_callable=AsyncMock) as mock_ai:
            mock_ai.return_value = json.dumps([
                {"name": "total_users", "display_name": "总用户数", "calculation_logic": "count(*)"}
            ])

            response = await client.post(
                f"/api/portal/meta/v2/datasets/{ds_id}/metrics/recommend",
                headers={"X-API-Key": admin_api_key}
            )
            assert response.status_code == 200
            assert len(response.json()["data"]) == 1
            assert response.json()["data"][0]["name"] == "total_users"
    finally:
        await client.delete(f"/api/portal/meta/v2/datasets/{ds_id}", headers={"X-API-Key": admin_api_key})

@pytest.mark.asyncio
async def test_get_yaml_api(client, admin_api_key):
    """测试 YAML 导出接口"""
    # 创建带表的数据集
    create_res = await client.post(
        "/api/portal/meta/v2/datasets",
        headers={"X-API-Key": admin_api_key},
        json={"name": "yaml_test", "data_source": "api_data"}
    )
    ds_id = create_res.json()["id"]

    try:
        # 保存一张表
        await client.post(
            f"/api/portal/meta/v2/datasets/{ds_id}/save-table",
            headers={"X-API-Key": admin_api_key},
            json={"physical_name": "test_table", "term": "测试", "columns": []}
        )

        response = await client.get(
            f"/api/portal/meta/v2/datasets/{ds_id}/yaml",
            headers={"X-API-Key": admin_api_key}
        )
        assert response.status_code == 200
        yaml_content = response.json()["data"]
        assert "dataset_name: yaml_test" in yaml_content
        assert "test_table" in yaml_content
    finally:
        await client.delete(f"/api/portal/meta/v2/datasets/{ds_id}", headers={"X-API-Key": admin_api_key})
