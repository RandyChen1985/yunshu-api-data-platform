import pytest
from fastapi import HTTPException, status
from app.core.dependencies import require_permission

@pytest.mark.asyncio
async def test_require_permission_success():
    # Factory creates the dependency callable
    dep = require_permission("test:perm")
    
    # Mock user dict (what require_api_key would return)
    user_with_perm = {
        "role": "user",
        "permissions": {"elements": ["test:perm"]}
    }
    
    # Call it
    result = await dep(user=user_with_perm)
    assert result == user_with_perm

@pytest.mark.asyncio
async def test_require_permission_failure():
    dep = require_permission("test:perm")
    
    user_without_perm = {
        "role": "user",
        "permissions": {"elements": ["other:perm"]}
    }
    
    with pytest.raises(HTTPException) as exc:
        await dep(user=user_without_perm)
    assert exc.value.status_code == 403

@pytest.mark.asyncio
async def test_require_permission_admin_bypass():
    dep = require_permission("test:perm")
    
    admin_user = {
        "role": "admin",
        "permissions": {}
    }
    
    result = await dep(user=admin_user)
    assert result == admin_user