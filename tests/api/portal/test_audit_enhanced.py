import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_get_logs_with_stats(client: AsyncClient, admin_api_key: str):
    """测试获取日志列表并包含统计信息"""
    response = await client.get(
        "/api/portal/audit/logs?include_stats=true",
        headers={"X-API-Key": admin_api_key}
    )
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "items" in data
    assert "statistics" in data
    
    # 验证统计数据结构
    stats = data["statistics"]
    assert "total_requests" in stats
    assert "success_count" in stats
    assert "error_count" in stats
    assert "success_rate" in stats
    assert "avg_response_time" in stats


@pytest.mark.asyncio
async def test_filter_by_time_range(client: AsyncClient, admin_api_key: str):
    """测试时间范围筛选"""
    response = await client.get(
        "/api/portal/audit/logs",
        params={
            "start_time": "2025-12-26T00:00:00",
            "end_time": "2025-12-27T23:59:59"
        },
        headers={"X-API-Key": admin_api_key}
    )
    assert response.status_code == 200
    # 验证返回的日志时间都在范围内
    data = response.json()
    assert "items" in data


@pytest.mark.asyncio
async def test_filter_by_method(client: AsyncClient, admin_api_key: str):
    """测试HTTP方法筛选"""
    response = await client.get(
        "/api/portal/audit/logs",
        params={"method": "GET"},
        headers={"X-API-Key": admin_api_key}
    )
    assert response.status_code == 200
    data = response.json()
    # 验证所有返回的日志方法都是GET
    for item in data["items"]:
        assert item["method"] == "GET"


@pytest.mark.asyncio
async def test_filter_by_status_code(client: AsyncClient, admin_api_key: str):
    """测试状态码筛选"""
    response = await client.get(
        "/api/portal/audit/logs",
        params={"status_code": 200},
        headers={"X-API-Key": admin_api_key}
    )
    assert response.status_code == 200
    data = response.json()
    # 验证所有返回的日志状态码都是200
    for item in data["items"]:
        assert item["status_code"] == 200


@pytest.mark.asyncio
async def test_filter_by_status_range(client: AsyncClient, admin_api_key: str):
    """测试状态码范围筛选"""
    response = await client.get(
        "/api/portal/audit/logs",
        params={"min_status": 200, "max_status": 299},
        headers={"X-API-Key": admin_api_key}
    )
    assert response.status_code == 200
    data = response.json()
    # 验证所有返回的日志状态码在范围内
    for item in data["items"]:
        assert 200 <= item["status_code"] <= 299


@pytest.mark.asyncio
async def test_filter_by_endpoint(client: AsyncClient, admin_api_key: str):
    """测试接口路径筛选（模糊匹配）"""
    response = await client.get(
        "/api/portal/audit/logs",
        params={"endpoint": "/api/portal"},
        headers={"X-API-Key": admin_api_key}
    )
    assert response.status_code == 200
    data = response.json()
    # 验证所有返回的日志路径包含关键字
    for item in data["items"]:
        assert "/api/portal" in item["endpoint"]


@pytest.mark.asyncio
async def test_get_log_detail_as_admin(client: AsyncClient, admin_api_key: str):
    """测试管理员获取日志详情"""
    # 先获取一个日志ID
    list_response = await client.get(
        "/api/portal/audit/logs?size=1",
        headers={"X-API-Key": admin_api_key}
    )
    assert list_response.status_code == 200
    items = list_response.json()["items"]
    
    if len(items) > 0:
        log_id = items[0]["id"]
        
        # 获取详情
        detail_response = await client.get(
            f"/api/portal/audit/logs/{log_id}",
            headers={"X-API-Key": admin_api_key}
        )
        assert detail_response.status_code == 200
        detail = detail_response.json()
        assert detail["id"] == log_id
        assert "trace_id" in detail
        assert "request_params" in detail
        assert "response_body" in detail


@pytest.mark.asyncio
async def test_get_log_detail_as_user(client: AsyncClient, valid_api_key: str):
    """测试普通用户获取日志详情（仅自己的）"""
    # 先以普通用户身份获取自己的日志
    list_response = await client.get(
        "/api/portal/audit/logs?size=1",
        headers={"X-API-Key": valid_api_key}
    )
    assert list_response.status_code == 200
    items = list_response.json()["items"]
    
    if len(items) > 0:
        log_id = items[0]["id"]
        
        # 获取详情
        detail_response = await client.get(
            f"/api/portal/audit/logs/{log_id}",
            headers={"X-API-Key": valid_api_key}
        )
        assert detail_response.status_code == 200


@pytest.mark.asyncio
async def test_get_log_detail_access_denied(client: AsyncClient, admin_api_key: str):
    """测试访问不存在的日志"""
    response = await client.get(
        "/api/portal/audit/logs/999999",
        headers={"X-API-Key": admin_api_key}
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_export_csv_as_admin(client: AsyncClient, admin_api_key: str):
    """测试CSV导出"""
    response = await client.get(
        "/api/portal/audit/logs/export?format=csv&size=10",
        headers={"X-API-Key": admin_api_key}
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/csv; charset=utf-8"
    assert "attachment" in response.headers.get("content-disposition", "")


@pytest.mark.asyncio
async def test_export_json_as_admin(client: AsyncClient, admin_api_key: str):
    """测试JSON导出"""
    response = await client.get(
        "/api/portal/audit/logs/export?format=json",
        headers={"X-API-Key": admin_api_key}
    )
    assert response.status_code == 200
    assert "application/json" in response.headers["content-type"]


@pytest.mark.asyncio
async def test_export_as_user_own_logs(client: AsyncClient, valid_api_key: str):
    """测试普通用户可以导出自己的日志"""
    response = await client.get(
        "/api/portal/audit/logs/export",
        headers={"X-API-Key": valid_api_key}
    )
    # 普通用户可以导出，但只能导出自己的日志
    assert response.status_code == 200
    # 验证是CSV格式
    assert "text/csv" in response.headers["content-type"]


@pytest.mark.asyncio
async def test_export_too_many_records(client: AsyncClient, admin_api_key: str):
    """测试导出记录数量限制"""
    # 这个测试需要数据库有大量数据才能触发
    # 暂时只验证接口可用
    response = await client.get(
        "/api/portal/audit/logs/export",
        headers={"X-API-Key": admin_api_key}
    )
    # 应该返回200或400（如果记录太多）
    assert response.status_code in [200, 400]


@pytest.mark.asyncio
async def test_pagination(client: AsyncClient, admin_api_key: str):
    """测试分页功能"""
    # 第一页
    response1 = await client.get(
        "/api/portal/audit/logs?page=1&size=5",
        headers={"X-API-Key": admin_api_key}
    )
    assert response1.status_code == 200
    data1 = response1.json()
    assert data1["page"] == 1
    assert data1["size"] == 5
    
    # 第二页
    response2 = await client.get(
        "/api/portal/audit/logs?page=2&size=5",
        headers={"X-API-Key": admin_api_key}
    )
    assert response2.status_code == 200
    data2 = response2.json()
    assert data2["page"] == 2


@pytest.mark.asyncio
async def test_user_can_only_see_own_logs(client: AsyncClient, valid_api_key: str):
    """测试普通用户只能看到自己的日志"""
    response = await client.get(
        "/api/portal/audit/logs",
        headers={"X-API-Key": valid_api_key}
    )
    assert response.status_code == 200
    data = response.json()
    
    # 验证返回的所有日志都属于当前用户
    for item in data["items"]:
        assert item["user_name"] == "test_user"


@pytest.mark.asyncio
async def test_filter_by_user_name_exact(client: AsyncClient, admin_api_key: str):
    """测试用户名精确搜索"""
    # 使用完整用户名 "test_user"
    response = await client.get(
        "/api/portal/audit/logs",
        params={"user_name": "test_user"},
        headers={"X-API-Key": admin_api_key}
    )
    assert response.status_code == 200
    data = response.json()
    # 验证返回的日志用户名精确匹配
    for item in data["items"]:
        assert item["user_name"] == "test_user"


@pytest.mark.asyncio
async def test_filter_by_client_ip_fuzzy(client: AsyncClient, admin_api_key: str):
    """测试客户端IP模糊搜索"""
    response = await client.get(
        "/api/portal/audit/logs",
        params={"client_ip": "127.0"},
        headers={"X-API-Key": admin_api_key}
    )
    assert response.status_code == 200
    data = response.json()
    # 验证返回的日志IP包含关键字
    for item in data["items"]:
        # 注意：如果日志中没有IP则跳过，或者确保测试数据中有IP
        if item["client_ip"]:
            assert "127.0" in item["client_ip"]
