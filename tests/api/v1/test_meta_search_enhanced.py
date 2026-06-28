import pytest
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock

@pytest.mark.asyncio
async def test_v1_search_keyword_basic(client: AsyncClient, admin_api_key: str):
    """验证 V1 关键词搜索基本流程"""
    mock_results = [
        {"item_type": "table", "item_id": 1, "dataset_id": 10, "reason": "Match table"}
    ]
    
    with patch("app.services.metadata_v2_service.MetadataV2Service.keyword_search", new_callable=AsyncMock) as mock_search, \
         patch("app.services.metadata_v2_service.MetadataV2Service.get_table_by_id", new_callable=AsyncMock) as mock_get_table, \
         patch("app.services.metadata_yaml_service.MetadataYamlService.generate_table_yaml") as mock_gen_yaml:
        
        mock_search.return_value = mock_results
        mock_get_table.return_value = {"id": 1, "physical_name": "test_table"}
        mock_gen_yaml.return_value = "table: test_table\n"
        
        response = await client.post(
            "/api/v1/meta/search",
            json={"query": "test", "search_type": "keyword"},
            headers={"X-API-Key": admin_api_key}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "table: test_table" in data["data"]
        assert data["count"] == 1
        assert 10 in data["dataset_ids"]
        # 确保不包含调试日志
        assert "debug_logs" not in data

@pytest.mark.asyncio
async def test_v1_search_semantic_basic(client: AsyncClient, admin_api_key: str):
    """验证 V1 语义搜索基本流程"""
    mock_results = [
        {
            "dataset_id": 20, 
            "item_type": "table", 
            "item_id": 2, 
            "reasons": "Semantic match",
            "yaml_content": "table: semantic_table\n"
        }
    ]
    
    with patch("app.services.vector_service.VectorService.semantic_search", new_callable=AsyncMock) as mock_vector:
        mock_vector.return_value = mock_results
        
        response = await client.post(
            "/api/v1/meta/search",
            json={"query": "hello", "search_type": "semantic", "enable_rerank": True},
            headers={"X-API-Key": admin_api_key}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "table: semantic_table" in data["data"]
        assert 20 in data["dataset_ids"]
        assert mock_vector.called
        # 检查参数传递
        args, kwargs = mock_vector.call_args
        assert kwargs["enable_rerank"] is True

@pytest.mark.asyncio
async def test_v1_search_permission_denied(client: AsyncClient):
    """验证 V1 搜索权限校验"""
    # 使用一个没有资源权限的普通用户 API Key
    # 注意：在测试环境中，我们可能需要模拟 PermissionService 或使用特定的测试账号
    
    with patch("app.services.permission_service.PermissionService.get_user_permissions", new_callable=AsyncMock) as mock_perms:
        from app.schemas.auth import UserPermissionsResponse, PermissionSet
        mock_perms.return_value = UserPermissionsResponse(
            user_id=999,
            username="poor_user",
            role="user",
            business_roles=[],
            permissions=PermissionSet(menus=[], elements=[], resources=[], datasources=[], data_tables=[])
        )
        
        # 模拟 require_api_key 返回一个普通用户
        with patch("app.services.auth_service.AuthService.verify_api_key", new_callable=AsyncMock) as mock_auth:
            mock_auth.return_value = {"user_id": 999, "user_name": "poor_user", "role": "user"}
            
            response = await client.post(
                "/api/v1/meta/search",
                json={"query": "secret"},
                headers={"X-API-Key": "some_key"}
            )
            
            assert response.status_code == 403
            assert "Permission Denied" in response.json()["detail"]

from unittest.mock import MagicMock
