import asyncio
from asynch.connection import Connection

async def test():
    try:
        conn = Connection(
            host='localhost', 
            port=9000, 
            user='admin', 
            password='admin123', 
            database='default'
        )
        await conn.connect()
        print('SUCCESS! ✅')
        await conn.close()
    except Exception as e:
        print(f'FAILED: {e}')

if __name__ == "__main__":
    asyncio.run(test())
