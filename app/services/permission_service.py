from typing import List, Dict, Any, Set
from app.core.database import get_db_connection
from app.schemas.auth import UserPermissionsResponse, PermissionSet
from app.core.redis import get_redis
import json
import logging

logger = logging.getLogger(__name__)

class PermissionService:
    @classmethod
    async def _get_cache_key(cls, user_id: int) -> str:
        return f"sys:auth:permissions:v2:user:{user_id}"

    @classmethod
    async def invalidate_user_cache(cls, user_id: int):
        """Force clear permission and user data cache for a specific user"""
        r = await get_redis()
        if r:
            # 1. Clear Permission Cache
            key = await cls._get_cache_key(user_id)
            await r.delete(key)
            
            # 2. Clear Auth Cache (Need to find the hashed key first)
            async with get_db_connection() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute("SELECT api_key_hash FROM api_users WHERE id = %s", (user_id,))
                    row = await cursor.fetchone()
                    if row and row[0]:
                        await r.delete(f"auth:api_key:{row[0]}")
            
            logger.info(f"Invalidated all caches for user {user_id}")

    @classmethod
    async def invalidate_role_cache(cls, role_id: int):
        """Clear cache for all users belonging to this role"""
        async with get_db_connection() as conn:
            async with conn.cursor() as cursor:
                # Get all user IDs in this role
                await cursor.execute("SELECT user_id FROM sys_user_role_relation WHERE role_id = %s", (role_id,))
                user_ids = [r[0] for r in await cursor.fetchall()]
                
                # Also find users who have this role as their PRIMARY role string in api_users
                await cursor.execute("SELECT role_code FROM sys_roles WHERE id = %s", (role_id,))
                role_row = await cursor.fetchone()
                if role_row:
                    role_code = role_row[0]
                    await cursor.execute("SELECT id FROM api_users WHERE role = %s", (role_code,))
                    user_ids.extend([r[0] for r in await cursor.fetchall()])
                
                user_ids = list(set(user_ids)) # Unique
                
                for uid in user_ids:
                    await cls.invalidate_user_cache(uid)
                
                logger.info(f"Invalidated cache for {len(user_ids)} users associated with role {role_id}")

    @classmethod
    async def get_user_permissions(cls, user_id: int) -> UserPermissionsResponse:
        """
        Aggregate permissions from:
        1. System Role (admin has all)
        2. Direct UI Permissions (menus, elements)
        3. Direct Resource Permissions (sys_user_resources)
        4. Role-based Permissions (inherited from sys_roles)
        """
        cache_key = await cls._get_cache_key(user_id)
        r = await get_redis()
        
        # 1. Try Cache
        if r:
            cached = await r.get(cache_key)
            if cached:
                try:
                    return UserPermissionsResponse(**json.loads(cached))
                except: pass

        async with get_db_connection() as conn:
            async with conn.cursor() as cursor:
                # 1. Fetch User Basic Info
                await cursor.execute("SELECT user_name, role FROM api_users WHERE id = %s", (user_id,))
                user_row = await cursor.fetchone()
                if not user_row:
                    raise ValueError(f"User {user_id} not found")
                
                username, sys_role = user_row
                
                # 2. If Admin, bypass specific checks
                if sys_role == 'admin':
                    return await cls._get_admin_full_permissions(user_id, username)

                # 3. Fetch Business Roles
                await cursor.execute("""
                    SELECT r.role_code, r.id 
                    FROM sys_roles r
                    JOIN sys_user_role_relation ur ON r.id = ur.role_id
                    WHERE ur.user_id = %s
                """, (user_id,))
                role_rows = await cursor.fetchall()
                business_roles = [r[0] for r in role_rows]
                role_ids = [r[1] for r in role_rows]

                # 4. Initialize Permission Set
                perm_set = PermissionSet(menus=[], elements=[], resources=[], datasources=[], data_tables=[])

                # 5. Fetch Direct Resource Permissions
                await cursor.execute("SELECT resource_key FROM sys_user_resources WHERE user_id = %s", (user_id,))
                res_rows = await cursor.fetchall()
                perm_set.resources = [r[0] for r in res_rows]

                # 6. Fetch UI & Data Asset Permissions (Direct + Role-based)
                ui_query = """
                    SELECT DISTINCT perm_type, perm_code 
                    FROM sys_ui_permissions 
                    WHERE enabled = 1 AND (user_id = %s
                """
                params = [user_id]
                if role_ids:
                    placeholders = ', '.join(['%s'] * len(role_ids))
                    ui_query += f" OR role_id IN ({placeholders})"
                    params.extend(role_ids)
                ui_query += ")"
                
                await cursor.execute(ui_query, tuple(params))
                ui_rows = await cursor.fetchall()
                
                for p_type, p_code in ui_rows:
                    if p_type == 'menu':
                        perm_set.menus.append(p_code)
                    elif p_type == 'element':
                        perm_set.elements.append(p_code)
                    elif p_type == 'resource':
                        perm_set.resources.append(p_code)
                    elif p_type == 'datasource':
                        # Ensure ds: prefix for consistency with admin logic and frontend
                        full_code = p_code if p_code.startswith("ds:") else f"ds:{p_code}"
                        perm_set.datasources.append(full_code)
                    elif p_type == 'data_table':
                        # Ensure ds: prefix
                        full_code = p_code if p_code.startswith("ds:") else f"ds:{p_code}"
                        perm_set.data_tables.append(full_code)

                # 7. Final Result Construction
                perm_set.resources = list(set(perm_set.resources))
                perm_set.datasources = list(set(perm_set.datasources))
                perm_set.data_tables = list(set(perm_set.data_tables))
                res = UserPermissionsResponse(
                    user_id=user_id,
                    username=username,
                    role=sys_role,
                    business_roles=business_roles,
                    permissions=perm_set
                )
                
                # 8. Cache result
                if r:
                    await r.setex(cache_key, 3600, res.model_dump_json())
                
                return res

    @classmethod
    async def _get_admin_full_permissions(cls, user_id: int, username: str) -> UserPermissionsResponse:
        """Admins get everything registered in sys_ui_permissions and sys_resource_meta"""
        async with get_db_connection() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("SELECT DISTINCT perm_type, perm_code FROM sys_ui_permissions")
                ui_rows = await cursor.fetchall()
                await cursor.execute("SELECT resource_key FROM sys_resource_meta")
                res_rows = await cursor.fetchall()
                await cursor.execute("SELECT source_name FROM sys_data_source")
                ds_rows = await cursor.fetchall()
                
                perm_set = PermissionSet(
                    menus=[], 
                    elements=[], 
                    resources=[r[0] for r in res_rows],
                    datasources=[f"ds:{r[0]}" for r in ds_rows],
                    data_tables=[f"ds:{r[0]}:table:*" for r in ds_rows]
                )
                for p_type, p_code in ui_rows:
                    if p_type == 'menu': perm_set.menus.append(p_code)
                    elif p_type == 'element': perm_set.elements.append(p_code)
                
                return UserPermissionsResponse(
                    user_id=user_id,
                    username=username,
                    role='admin',
                    business_roles=['SUPER_ADMIN'],
                    permissions=perm_set
                )