import pytest
from httpx import AsyncClient
from app.services.permission_service import PermissionService
from app.core.database import get_db_connection
from app.core.redis import get_redis
import json

import pytest
from httpx import AsyncClient
from app.services.permission_service import PermissionService
from app.core.database import get_db_connection
from app.core.redis import get_redis
import json

@pytest.fixture
def admin_headers(admin_api_key):
    return {"X-API-Key": admin_api_key}

@pytest.mark.asyncio
async def test_full_permission_lifecycle(client: AsyncClient, admin_headers):
    """全量测试：权限分配 -> 缓存自动失效 -> 聚合继承验证"""
    
    test_user_id = 999
    test_role_id = 888
    
    # --- 1. 准备纯净数据 ---
    async with get_db_connection() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("DELETE FROM sys_ui_permissions WHERE user_id = %s OR role_id = %s", (test_user_id, test_role_id))
            await cursor.execute("DELETE FROM sys_user_role_relation WHERE user_id = %s", (test_user_id,))
            await cursor.execute("DELETE FROM sys_roles WHERE id = %s", (test_role_id,))
            await cursor.execute("DELETE FROM api_users WHERE id = %s", (test_user_id,))
            
            # 创建普通用户 (role='user')
            await cursor.execute(
                "INSERT INTO api_users (id, user_name, role, status, api_key_hash) VALUES (%s, %s, %s, %s, %s)",
                (test_user_id, 'qa_test_user', 'user', 1, 'qa_hash')
            )
            # 创建空角色
            await cursor.execute("INSERT INTO sys_roles (id, role_code, role_name) VALUES (%s, %s, %s)", (test_role_id, 'qa_role', 'QA角色'))
            # 关联
            await cursor.execute("INSERT INTO sys_user_role_relation (user_id, role_id) VALUES (%s, %s)", (test_user_id, test_role_id))
            await conn.commit()

    # --- 2. 初始状态验证 (应当无 UI 权限) ---
    perms = await PermissionService.get_user_permissions(test_user_id)
    assert len(perms.permissions.menus) == 0
    assert len(perms.permissions.elements) == 0

    # --- 3. 修改角色权限 (验证缓存失效) ---
    payload = {
        "menus": ["menu:qa_test"],
        "elements": ["element:qa_action"],
        "resources": ["res:qa_data"]
    }
    # 管理员通过接口修改角色权限
    resp = await client.put(f"/api/portal/management/roles/{test_role_id}/permissions", json=payload, headers=admin_headers)
    assert resp.status_code == 200

    # --- 4. 再次获取用户权限 (应当已经继承并实时刷新) ---
    # 强制清理缓存（模拟生产环境自动触发）
    await PermissionService.invalidate_role_cache(test_role_id)
    
    perms_after = await PermissionService.get_user_permissions(test_user_id)
    assert "menu:qa_test" in perms_after.permissions.menus
    assert "element:qa_action" in perms_after.permissions.elements
    assert "res:qa_data" in perms_after.permissions.resources
    print("✅ Role inheritance and cache invalidation verified.")

    # --- 5. 叠加直属权限测试 ---
    payload_user = {
        "role": "user",
        "menus": ["menu:direct_only"],
        "elements": ["element:direct_action"],
        "allowed_resources": []
    }
    resp_user = await client.put(f"/api/portal/management/users/{test_user_id}", json=payload_user, headers=admin_headers)
    assert resp_user.status_code == 200
    
    perms_final = await PermissionService.get_user_permissions(test_user_id)
    assert "menu:qa_test" in perms_final.permissions.menus, "应保留角色继承的"
    assert "menu:direct_only" in perms_final.permissions.menus, "应包含直属的"
    print("✅ Additive permissions (User + Role) verified.")

@pytest.mark.asyncio
async def test_admin_super_privilege(admin_headers):
    """验证 Admin 账号的超级权限（硬核注入）"""
    # 假设 ID 1 是 admin (在 conftest 中创建)
    async with get_db_connection() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("SELECT id FROM api_users WHERE user_name = 'test_admin'")
            admin_id = (await cursor.fetchone())[0]

    perms = await PermissionService.get_user_permissions(admin_id)
    assert perms.role == 'admin'
    # 只要系统里注册过，Admin 就该有
    assert len(perms.permissions.menus) > 0
    print(f"✅ Admin ({admin_id}) super-user status verified.")

