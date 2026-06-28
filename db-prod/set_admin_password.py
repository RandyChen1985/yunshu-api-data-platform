
import asyncio
import sys
import os
import bcrypt

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import get_db_connection

async def set_admin_password():
    print("Setting admin password...")
    password = "admin123"
    # Using bcrypt directly to avoid passlib complexity for this simple script if it fails
    hashed_bytes = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    hashed_password = hashed_bytes.decode('utf-8')
    
    async with get_db_connection() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(
                "UPDATE api_users SET password_hash = %s WHERE user_name = 'admin'",
                (hashed_password,)
            )
            print(f"Updated {cursor.rowcount} rows.")
            
    print(f"Admin password set to: {password}")

if __name__ == "__main__":
    asyncio.run(set_admin_password())
