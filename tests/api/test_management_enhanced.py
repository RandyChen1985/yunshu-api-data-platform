import pytest
from httpx import AsyncClient
from app.core.database import get_db_connection

@pytest.mark.asyncio
async def test_role_member_management(client: AsyncClient, admin_api_key: str):
    """Test GET and PUT role member endpoints"""
    headers = {"X-API-Key": admin_api_key}
    
    # 1. Prepare Test Data: Create a role and two users
    async with get_db_connection() as conn:
        async with conn.cursor() as cursor:
            # Create Role
            role_code = "test_member_role"
            await cursor.execute("DELETE FROM sys_roles WHERE role_code = %s", (role_code,))
            await cursor.execute(
                "INSERT INTO sys_roles (role_code, role_name, description) VALUES (%s, %s, %s)",
                (role_code, "Test Member Role", "Testing role membership assignment")
            )
            await cursor.execute("SELECT last_insert_id()")
            role_id = (await cursor.fetchone())[0]
            
            # Create Users
            users = [("user_member_1", "user"), ("user_member_2", "user")]
            user_ids = []
            for name, role in users:
                await cursor.execute("DELETE FROM api_users WHERE user_name = %s", (name,))
                await cursor.execute(
                    "INSERT INTO api_users (user_name, role, status, api_key_hash) VALUES (%s, %s, 1, %s)",
                    (name, role, f"fake_hash_{name}")
                )
                await cursor.execute("SELECT last_insert_id()")
                user_ids.append((await cursor.fetchone())[0])
            
            await conn.commit()

    try:
        # 2. Test GET members (should be empty)
        response = await client.get(f"/api/portal/management/roles/{role_id}/users", headers=headers)
        assert response.status_code == 200
        assert response.json() == []
        
        # 3. Test PUT members (Assign both users)
        payload = {"user_ids": user_ids}
        response = await client.put(f"/api/portal/management/roles/{role_id}/users", headers=headers, json=payload)
        assert response.status_code == 200
        assert response.json()["message"] == "Role members updated successfully"
        
        # Verify via GET
        response = await client.get(f"/api/portal/management/roles/{role_id}/users", headers=headers)
        assert response.status_code == 200
        # Order might vary depending on DB, but for IDs usually consistent
        assert sorted(response.json()) == sorted(user_ids)
        
        # 4. Test PUT members (Remove one user)
        payload = {"user_ids": [user_ids[0]]}
        response = await client.put(f"/api/portal/management/roles/{role_id}/users", headers=headers, json=payload)
        assert response.status_code == 200
        
        # Verify removal
        response = await client.get(f"/api/portal/management/roles/{role_id}/users", headers=headers)
        assert response.json() == [user_ids[0]]
        
        # 5. Test Error Handling: Invalid user ID
        payload = {"user_ids": [user_ids[0], 999999]}
        response = await client.put(f"/api/portal/management/roles/{role_id}/users", headers=headers, json=payload)
        assert response.status_code == 400
        assert "invalid" in response.json()["detail"].lower()
        
    finally:
        # Cleanup
        async with get_db_connection() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("DELETE FROM sys_user_role_relation WHERE role_id = %s", (role_id,))
                await cursor.execute("DELETE FROM sys_roles WHERE id = %s", (role_id,))
                for uid in user_ids:
                    await cursor.execute("DELETE FROM api_users WHERE id = %s", (uid,))
                await conn.commit()
