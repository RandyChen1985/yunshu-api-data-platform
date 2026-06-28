import asyncio
import sys
import os

# 将项目根目录添加到路径
sys.path.append(os.getcwd())

from app.core import redis
from app.services.vector_service import VectorService

async def main():
    print("🚀 开始重置 Redis 向量索引...")
    await redis.init_redis()
    r = await redis.get_redis()
    if not r:
        print("❌ 无法连接到 Redis")
        return

    # 1. 删除旧索引
    try:
        await r.execute_command("FT.DROPINDEX", VectorService.INDEX_NAME)
        print(f"✅ 成功删除索引: {VectorService.INDEX_NAME}")
    except Exception as e:
        print(f"⚠️ 删除索引失败 (可能不存在): {e}")

    # 2. 创建新索引
    try:
        await VectorService.ensure_index()
        print(f"✅ 成功创建最新 Schema 的索引: {VectorService.INDEX_NAME}")
    except Exception as e:
        print(f"❌ 创建索引失败: {e}")

    await redis.close_redis()
    print("✨ 重置完成")

if __name__ == "__main__":
    asyncio.run(main())
