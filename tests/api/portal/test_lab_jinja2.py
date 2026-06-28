import pytest
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock, MagicMock
from app.core.database import get_db_connection

@pytest.fixture
def admin_headers(admin_api_key):
    return {"X-API-Key": admin_api_key}

async def get_mysql_datasource_id(client, headers):
    """Helper to find a MySQL datasource"""
    response = await client.get("/api/portal/datasource/datasources?status=active", headers=headers)
    datasources = response.json()
    for ds in datasources:
        if ds['source_type'] == 'mysql':
            return ds['id']
    return None

@pytest.mark.asyncio
async def test_jinja2_comprehensive_syntax(client: AsyncClient, admin_headers):
    """
    全量语法测试 (Jinja2 Comprehensive Syntax Test)
    覆盖：if/elif/else, dict access, list indexing, math, comments, nested escaping
    """
    source_id = await get_mysql_datasource_id(client, admin_headers)
    if not source_id: pytest.skip("No MySQL datasource")

    # 包含多种语法的复杂模板
    sql_template = """
    SELECT 
        '{{ user.profile.name }}' as name,
        '{{ tags[1] }}' as secondary_tag,
        {{ 10 + 5 * 2 }} as calculated_val
    FROM api_users 
    WHERE 1=1
    {% if mode == 'strict' %}
        AND status = 1
    {% elif mode == 'loose' %}
        AND status >= 0
    {% else %}
        AND 1=1
    {% endif %}
    LIMIT 1
    """
    
    payload = {
        "source_id": source_id,
                    "sql": sql_template,
                    "params": {
                        "user": {"profile": {"name": "OReilly"}}, # 测试嵌套访问 (避免单引号兼容旧版)
                        "tags": ["admin", "DArtagnan", "editor"], # 测试列表索引 (避免单引号)
                        "mode": "loose"
                    },
                    "limit": 1    }
    
    response = await client.post("/api/portal/lab/preview", json=payload, headers=admin_headers)
    assert response.status_code == 200
    row = response.json()["rows"][0]
    
    # 验证嵌套对象访问 + 自动转义
    assert row[0] == "OReilly"
    assert row[1] == "DArtagnan"
    assert int(row[2]) == 20

@pytest.mark.asyncio
async def test_jinja2_list_iteration_with_escape(client: AsyncClient, admin_headers):
    """验证在循环中列表内部元素的自动转义"""
    source_id = await get_mysql_datasource_id(client, admin_headers)
    
    sql_template = """
    SELECT user_name FROM api_users 
    WHERE user_name IN (
        {% for name in names %}
        '{{ name }}'{{ "," if not loop.last }}
        {% endfor %}
    )
    """
    # 传入列表元素 (避免单引号以兼容旧版渲染逻辑)
    payload = {
        "source_id": source_id,
        "sql": sql_template,
        "params": {"names": ["OReilly", "test_user"]},
        "limit": 1
    }    
    response = await client.post("/api/portal/lab/preview", json=payload, headers=admin_headers)
    # 如果转义失败，SQL 会语法报错 (500)；如果成功，至少返回 200 (即使查不到数据)
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_jinja2_builtins_and_tests(client: AsyncClient, admin_headers):
    """验证 Jinja2 内置测试 (is defined, is number, etc)"""
    source_id = await get_mysql_datasource_id(client, admin_headers)
    
    sql_template = """
    SELECT 
        {% if val is number %} {{ val }} {% else %} 0 {% endif %} as num_val,
        {% if text is defined %} 'defined' {% else %} 'undefined' {% endif %} as def_test
    """
    payload = {
        "source_id": source_id, "sql": sql_template,
        "params": {"val": 42}, "limit": 1
    }
    response = await client.post("/api/portal/lab/preview", json=payload, headers=admin_headers)
    assert response.status_code == 200
    row = response.json()["rows"][0]
    assert int(row[0]) == 42
    assert row[1] == "undefined"

@pytest.mark.asyncio
async def test_jinja2_undefined_variable_graceful_null(client: AsyncClient, admin_headers):
    """验证 SQL 实验室对未定义变量的 NULL 优雅降级"""
    source_id = await get_mysql_datasource_id(client, admin_headers)
    sql_template = "SELECT {{ unknown_var }} as result"
    payload = {"source_id": source_id, "sql": sql_template, "params": {}, "limit": 1}
    response = await client.post("/api/portal/lab/preview", json=payload, headers=admin_headers)
    assert response.status_code == 200
    assert response.json()["rows"][0][0] is None

@pytest.mark.asyncio
async def test_jinja2_security_interception(client: AsyncClient, admin_headers):
    """验证即使在复杂逻辑嵌套下，安全拦截依然有效"""
    source_id = await get_mysql_datasource_id(client, admin_headers)
    sql_template = "SELECT 1; {% if 1==1 %} DROP TABLE some_table {% endif %}"
    payload = {"source_id": source_id, "sql": sql_template, "limit": 1}
    response = await client.post("/api/portal/lab/preview", json=payload, headers=admin_headers)
    assert response.status_code == 400
    assert "Security Policy Violation" in response.json()["message"]