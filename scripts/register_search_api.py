import asyncio
import logging
from app.core.database import get_db_connection

logging.basicConfig(level=logging.INFO)

async def register_search_resource():
    async with get_db_connection() as conn:
        async with conn.cursor() as cursor:
            # 1. 检查是否已存在
            resource_key = 'system.metadata.search'
            await cursor.execute("SELECT id FROM sys_resource_meta WHERE resource_key = %s", (resource_key,))
            exists = await cursor.fetchone()
            
            if exists:
                logging.info(f"Resource {resource_key} already exists.")
                return

            # 2. 插入新资源
            # 模仿 system.sql.execute 的配置
            sql = """
                INSERT INTO sys_resource_meta (
                    resource_key, resource_name, resource_mode, resource_group, 
                    description, status, data_source
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            values = (
                resource_key,
                '语义元数据检索',
                'SQL',  # 借用 SQL 模式，因为它是原子接口
                'System',
                '支持外部系统通过关键词或语义召回 RAG 上下文 (YAML)',
                1,      # Active
                'default'
            )
            
            await cursor.execute(sql, values)
            logging.info(f"Successfully registered resource: {resource_key}")

if __name__ == "__main__":
    asyncio.run(register_search_resource())
