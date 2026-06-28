import sys
import asyncio
import os

# Ensure app is in pythonpath
sys.path.append(os.getcwd())

from app.core import database

async def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/run_migration.py <sql_file>")
        sys.exit(1)
    
    sql_file = sys.argv[1]
    if not os.path.exists(sql_file):
         print(f"❌ File not found: {sql_file}")
         sys.exit(1)

    print(f"Applying {sql_file}...")
    
    with open(sql_file, 'r') as f:
        sql_content = f.read()

    # Filter out empty statements
    statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
        
    await database.init_db()
    try:
        async with database.get_db_connection() as conn:
            async with conn.cursor() as cursor:
                for sql in statements:
                    await cursor.execute(sql)
                await conn.commit()
        print(f"✅ Successfully executed {len(statements)} statements.")
    except Exception as e:
        print(f"❌ Execution failed: {e}")
        sys.exit(1)
    finally:
        await database.close_db()

if __name__ == "__main__":
    asyncio.run(main())
