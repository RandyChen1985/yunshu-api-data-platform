import asyncio
from app.core.database import get_db_connection

async def seed_roles():
    async with get_db_connection() as conn:
        async with conn.cursor() as cursor:
            roles = [
                ('developer', '开发人员', '拥有实验室和接口管理权限'),
                ('operator', '运维人员', '拥有数据源和审计权限'),
                ('auditor', '安全审计员', '仅拥有审计日志查看权限')
            ]
            await cursor.executemany(
                "INSERT IGNORE INTO sys_roles (role_code, role_name, description) VALUES (%s, %s, %s)",
                roles
            )
            await conn.commit()
            print("✅ Roles seeded successfully.")

if __name__ == "__main__":
    asyncio.run(seed_roles())
