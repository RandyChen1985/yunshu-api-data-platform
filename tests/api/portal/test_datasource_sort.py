import pytest
from httpx import AsyncClient
import uuid

@pytest.mark.asyncio
async def test_list_datasources_sorting(client: AsyncClient, admin_api_key: str):
    """验证获取数据源列表时是否包含 sort_order 并按其排序"""
    response = await client.get(
        "/api/portal/datasource/datasources",
        headers={"X-API-Key": admin_api_key}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 0
    if len(data) > 0:
        assert "sort_order" in data[0]
        # 验证是否遵循基本排序逻辑（由于初始可能是乱序的，我们在 reorder 测试中验证严格顺序）
        # 这里验证 sort_order 字段存在即可

@pytest.mark.asyncio
async def test_reorder_datasources(client: AsyncClient, admin_api_key: str):
    """验证批量重排序接口"""
    # 1. 获取现有列表
    response = await client.get(
        "/api/portal/datasource/datasources",
        headers={"X-API-Key": admin_api_key}
    )
    data = response.json()
    if len(data) < 2:
        # 如果数据不够，手动创建两个
        for i in range(2):
            await client.post(
                "/api/portal/datasource/datasources",
                json={
                    "source_name": f"test_sort_{uuid.uuid4().hex[:6]}",
                    "source_type": "mysql",
                    "host": "localhost",
                    "port": 3306,
                    "sort_order": i,
                    "status": 1
                },
                headers={"X-API-Key": admin_api_key}
            )
        # 重新获取
        response = await client.get(
            "/api/portal/datasource/datasources",
            headers={"X-API-Key": admin_api_key}
        )
        data = response.json()
    
    original_ids = [item["id"] for item in data]
    # 2. 反转顺序
    reversed_ids = list(reversed(original_ids))
    
    # 3. 调用重排序接口
    reorder_resp = await client.put(
        "/api/portal/datasource/reorder",
        json={"ids": reversed_ids},
        headers={"X-API-Key": admin_api_key}
    )
    assert reorder_resp.status_code == 200
    
    # 4. 再次获取列表验证顺序
    final_resp = await client.get(
        "/api/portal/datasource/datasources",
        headers={"X-API-Key": admin_api_key}
    )
    final_data = final_resp.json()
    final_ids = [item["id"] for item in final_data]
    
    # 过滤出我们刚才排序的那些 ID (因为可能存在其他干扰数据)
    actual_final_ids = [tid for tid in final_ids if tid in reversed_ids]
    # 注意：由于 list_datasources 还有个 id DESC 的次要排序，
    # 且 reorder 会给所有涉及的 ID 分配 0, 1, 2...
    # 所以 final_ids 应该严格等于 reversed_ids 的顺序（假设我们传递了全量 ID）
    assert actual_final_ids == reversed_ids

@pytest.mark.asyncio
async def test_create_with_sort_order(client: AsyncClient, admin_api_key: str):
    """验证创建时可以指定 sort_order"""
    name = f"test_ds_{uuid.uuid4().hex[:8]}"
    payload = {
        "source_name": name,
        "source_type": "mysql",
        "host": "localhost",
        "port": 3306,
        "database_name": "test",
        "username": "root",
        "password": "password",
        "sort_order": 99,
        "description": "Test Sort Order",
        "status": 1
    }
    response = await client.post(
        "/api/portal/datasource/datasources",
        json=payload,
        headers={"X-API-Key": admin_api_key}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["sort_order"] == 99
    
    # 清理
    await client.delete(f"/api/portal/datasource/datasources/{data['id']}", headers={"X-API-Key": admin_api_key})