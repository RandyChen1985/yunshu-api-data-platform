import asyncio
import os
import sys

# Ensure app path is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings
import aiomysql

async def apply_migration():
    print(f"Applying migration to {settings.MYSQL_DB}...")
    
    # Read SQL file
    if len(sys.argv) > 1:
        sql_file = sys.argv[1]
    else:
        sql_file = "db-prod/V1-dynamic_resource_config.sql"
        
    print(f"Reading SQL file: {sql_file}")

    if not os.path.exists(sql_file):
        print(f"Error: {sql_file} not found")
        return

    with open(sql_file, "r", encoding="utf-8") as f:
        sql_content = f.read()

    # Create connection
    try:
        pool = await aiomysql.create_pool(
            host=settings.MYSQL_HOST,
            port=settings.MYSQL_PORT,
            user=settings.MYSQL_USER,
            password=settings.MYSQL_PASSWORD,
            db=settings.MYSQL_DB,
            autocommit=True
        )
    except Exception as e:
        print(f"Failed to connect to DB: {e}")
        return

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            # Split by semicolon simple logic (assuming no semicolons in strings for this specific file)
            # The SQL file has INSERTs with strings. Semicolon splitting is dangerous if strings contain semicolons.
            # However, for this specific seed file, I know the content.
            # Better approach: Read explicit statements if possible, or use Client that supports multi=True?
            # aiomysql execute() usually creates prepared statement.
            # Let's try to parse carefully or just rely on simple split if confident.
            # My SQL file has `custom_sql` TEXT field ?
            # Wait, `db-prod/V1-dynamic_resource_config.sql` contents:
            # It has `custom_sql` column but seed data for custom_sql is empty or simple?
            # Let's check the SQL file content again to be sure.
            
            statements = []
            delimiter = ";"
            current_statement = ""
            
            for line in sql_content.splitlines():
                line = line.strip()
                if not line or line.startswith("--"):
                    continue
                current_statement += line + " "
                if line.endswith(delimiter):
                    statements.append(current_statement.strip())
                    current_statement = ""
            
            for stmt in statements:
                if not stmt: 
                    continue
                try:
                    await cursor.execute(stmt)
                    print(f"Executed: {stmt[:50]}...")
                except Exception as e:
                    print(f"Error executing statement: {stmt[:50]}... \nError: {e}")
                    # Don't return, try next? Or stop?
                    # Create table might fail if exists.
                    if "already exists" in str(e):
                        continue
                    # For Insert, if duplicate key?
                    if "Duplicate entry" in str(e):
                         print("Skipping duplicate entry.")
                         continue
                    
    pool.close()
    await pool.wait_closed()
    print("Migration finished.")

if __name__ == "__main__":
    asyncio.run(apply_migration())
