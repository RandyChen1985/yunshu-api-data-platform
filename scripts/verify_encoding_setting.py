
import asyncio
from asynch.pool import Pool

async def verify_encoding_arg():
    print("Attempting to initialize AsynchPool with encoding_errors='replace'...")
    try:
        # We don't need to actually connect, just see if __init__ accepts the arg
        # or if it crashes immediately. 
        # However, AsynchPool might just store kwargs and use them on connect().
        # So we might need to actually try to create a pool object.
        
        pool = Pool(
            host='localhost', 
            port=9000, 
            user='default', 
            password='', 
            database='default',
            encoding_errors='replace'
        )
        print("Success: AsynchPool accepted encoding_errors parameter.")
    except TypeError as e:
        print(f"Failure: AsynchPool raised TypeError: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(verify_encoding_arg())
