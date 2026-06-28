import asyncio
import os
from app.core import database

async def run_sql_file(filename):
    if not os.path.exists(filename):
        print(f"File {filename} not found")
        return

    with open(filename, 'r', encoding='utf-8') as f:
        sql = f.read()

    # Improved split logic: split by semicolon + newline
    import re
    # Remove single line comments
    sql = re.sub(r'--.*', '', sql)
    # Split by semicolon followed by optional whitespace and newline
    statements = [s.strip() for s in re.split(r';\s*\n', sql) if s.strip()]

    conn = await database.get_db_connection().__aenter__()
    try:
        async with conn.cursor() as cursor:
            for stmt in statements:
                print(f"Executing: {stmt[:50]}...")
                await cursor.execute(stmt)
            await conn.commit()
            print("Successfully executed all statements.")
    except Exception as e:
        print(f"Error executing SQL: {e}")
        await conn.rollback()
    finally:
        # await conn.close() # Connection is managed by context manager in app.core.database if it was get_db_connection()
        pass

if __name__ == "__main__":
    asyncio.run(run_sql_file("db-prod/V1-dynamic_resource_config.sql"))
