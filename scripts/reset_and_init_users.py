import asyncio
import sys
import os
import json

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core import database
from app.services.auth_service import AuthService
from app.core.config import settings

async def reset_and_init():
    print("🚀 开始重置数据库用户...")
    
    await database.init_db()
    
    async with database.get_db_connection() as conn:
        async with conn.cursor() as cursor:
            # 1. 清空数据
            print("🧹 清空 api_users 表...")
            await cursor.execute("TRUNCATE TABLE api_users")
            
            # 2. 创建管理员 (admin)
            print("👤 创建管理员账号 (admin)...")
            admin_key = await AuthService.generate_api_key(
                user_name="admin",
                role="admin",
                remark="超级管理员"
            )
            
            # 3. 创建普通用户 (demo_user)
            print("👤 创建普通用户 (demo_user)...")
            # 赋予普通用户所有资源的访问权限，方便测试
            all_resources = [
                "donghuan_real_metrics", "donghuan_events", 
                "yunshu_rooms", "yunshu_racks", "yunshu_device_points",
                "ccg_resources", "ccg_virtual_machines", "ccg_containers"
            ]
            perms_json = json.dumps({"allowed_resources": all_resources})
            
            # 先生成 API Key (auth_service 默认 permissions 是 None)
            user_key = await AuthService.generate_api_key(
                user_name="demo_user",
                role="user",
                remark="演示用户"
            )
            
            # 更新 demo_user 的权限
            await cursor.execute(
                "UPDATE api_users SET permissions = %s WHERE user_name = 'demo_user'",
                (perms_json,)
            )

    print("\n" + "="*50)
    print("✅ 重置完成！请使用以下 Key 登录：")
    print("="*50)
    print(f"👑 [Admin]     用户: admin")
    print(f"🔑 API Key:    {admin_key}")
    print("-" * 50)
    print(f"🧑 [User]      用户: demo_user")
    print(f"🔑 API Key:    {user_key}")
    print("="*50 + "\n")

    await database.close_db()

if __name__ == "__main__":
    try:
        asyncio.run(reset_and_init())
    except Exception as e:
        print(f"❌ 发生错误: {e}")
        # 如果是密码错误，提示用户
        if "Access denied" in str(e):
            print("\n⚠️  提示：无法连接数据库。")
            print("   请检查 .env 文件中的 MYSQL_PASSWORD 是否正确。")
