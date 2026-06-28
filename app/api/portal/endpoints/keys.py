from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional, Dict
from app.services.auth_service import AuthService
from app.core import database

from app.core.dependencies import require_admin

router = APIRouter()

# Schema for creating a key
class CreateKeyRequest(BaseModel):
    user_name: str
    role: Optional[str] = "user"  # Can be 'user' or 'admin'

class APIKeyResponse(BaseModel):
    code: int = 200
    message: str = "success"
    data: Dict[str, str]

@router.post("/", response_model=APIKeyResponse)
async def create_api_key(
    request: CreateKeyRequest,
    admin: dict = Depends(require_admin)
):
    """
    Create a new API Key.
    Admin only.
    """
    try:
        await database.init_db() # Ensure DB pool is ready if called independently (though main.py handles this)
        
        try:
            api_key = await AuthService.generate_api_key(request.user_name, role=request.role)
        except Exception as e:
            # Handle unique constraint violation (user_name exists)
            # Simplification: just assume success or error 500 for MVP
            raise e

        return {
            "code": 200,
            "message": "success",
            "data": {
                "user_name": request.user_name,
                "api_key": api_key,
                "role": request.role
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
