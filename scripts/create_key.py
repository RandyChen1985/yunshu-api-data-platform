import asyncio
from app.core import database
from app.services.auth_service import AuthService
import sys

async def create_key(username: str):
    await database.init_db()
    try:
        print(f"Generating key for user: {username}")
        api_key = await AuthService.generate_api_key(username)
        print(f"SUCCESS! API Key for '{username}':")
        print(f"\n{api_key}\n")
        print("Please save this key securely.")
    finally:
        await database.close_db()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python create_key.py <username>")
        sys.exit(1)
    asyncio.run(create_key(sys.argv[1]))
