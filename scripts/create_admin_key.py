import asyncio
from app.core import database
from app.services.auth_service import AuthService
import sys

async def create_admin_key(username: str = "admin"):
    await database.init_db()
    try:
        print(f"Generating ADMIN key for user: {username}")
        
        # Generate key with admin role
        api_key = await AuthService.generate_api_key(username, role="admin")
        
        print(f"\n{'='*60}")
        print(f"SUCCESS! Admin API Key Generated")
        print(f"{'='*60}")
        print(f"Username: {username}")
        print(f"API Key:  {api_key}")
        print(f"Role:     admin")
        print(f"{'='*60}")
        print("\n⚠️  Please save this key securely - it won't be shown again!")
        print("\nYou can use this key to login to the admin portal:")
        print(f"  Username: {username}")
        print(f"  API Key:  {api_key}")
        
    finally:
        await database.close_db()

if __name__ == "__main__":
    username = sys.argv[1] if len(sys.argv) > 1 else "admin"
    asyncio.run(create_admin_key(username))
