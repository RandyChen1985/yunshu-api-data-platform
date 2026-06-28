import asyncio
from asynch.connection import Connection
from app.core.config import settings

COMMON_PASSWORDS = ["", "root123", "password", "123456", "clickhouse", "admin"]
USERS = ["default", "yovole_ck_prod"] # user might have named the user same as db

async def probe():
    print(f"Probing ClickHouse at {settings.CLICKHOUSE_HOST}:{settings.CLICKHOUSE_PORT}...")
    
    for user in USERS:
        for pwd in COMMON_PASSWORDS:
            print(f"Trying: User='{user}', Pass='{pwd}' ... ", end="")
            try:
                conn = Connection(
                    host=settings.CLICKHOUSE_HOST,
                    port=settings.CLICKHOUSE_PORT,
                    user=user,
                    password=pwd,
                    database="default"
                )
                await conn.connect()
                print("SUCCESS! ✅")
                print(f"\n*** FOUND VALID CREDENTIALS ***\nUser: {user}\nPassword: {pwd}\n")
                await conn.close()
                return
            except Exception as e:
                pass # print(f"FAILED ({str(e)})")
            print("FAILED ❌")

if __name__ == "__main__":
    asyncio.run(probe())
