from fastapi import APIRouter, Depends, HTTPException, status, Response, Header
from typing import Optional
from pydantic import BaseModel, Field
from app.core.dependencies import require_api_key
from app.services.auth_service import AuthService

from app.services.permission_service import PermissionService
from app.schemas.auth import UserPermissionsResponse

router = APIRouter()

@router.get("/permissions", summary="获取用户权限集", response_model=UserPermissionsResponse)
async def get_my_permissions(
    user: dict = Depends(require_api_key)
):
    """
    聚合获取当前用户的所有权限，包括菜单、功能点和数据资源。
    支持角色继承。
    """
    user_id = int(user["user_id"])
    return await PermissionService.get_user_permissions(user_id)

class LoginRequest(BaseModel):

    api_key: Optional[str] = Field(None, description="API 密钥", example="S63B_4wMogHLKDhTDmdwaYFs2ubNDVLXq6Fp4egn0uQ")
    username: Optional[str] = Field(None, description="用户名", example="admin")
    password: Optional[str] = Field(None, description="密码", example="password123")

class SSOLoginRequest(BaseModel):
    username: str = Field(..., description="用户名", example="admin")
    password: str = Field(..., description="密码", example="password123")

class ChangePasswordRequest(BaseModel):
    old_password: Optional[str] = Field(None, description="旧密码 (如果已设置过密码则必填)")
    new_password: str = Field(..., description="新密码", min_length=6)

@router.post("/change-password", summary="修改密码")
async def change_password(
    request: ChangePasswordRequest,
    user: dict = Depends(require_api_key)
):
    """
    修改当前登录用户的密码。
    如果用户尚未设置过密码，则无需提供 old_password；
    如果已经设置过密码，则必须提供正确的 old_password。
    """
    user_id = user["user_id"]
    
    try:
        success = await AuthService.change_password(
            user_id, 
            request.new_password, 
            request.old_password
        )
        if not success:
             raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="密码修改失败"
            )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
        
    return {"status": "success", "message": "密码修改成功"}

@router.post("/login", summary="用户登录")
async def login(request: LoginRequest, response: Response):
    """
    用户登录接口
    
    支持 API Key 或 账号密码 登录。
    
    **请求参数：**
    - **api_key**: (可选) API 密钥
    - **username**: (可选) 用户名
    - **password**: (可选) 密码
    
    **响应示例：**
    ```json
    {
      "status": "success",
      "data": {
        "user_id": "1",
        "user_name": "admin",
        "role": "admin"
      }
    }
    ```
    
    **错误响应：**
    - `401 Unauthorized`: 认证失败
    - `400 Bad Request`: 缺少认证参数
    """
    user = None
    token = None
    
    if request.api_key:
        # API Key Login
        user = await AuthService.verify_api_key(request.api_key)
        token = request.api_key
    elif request.username and request.password:
        # Password Login
        user = await AuthService.authenticate_user(request.username, request.password)
        if user:
            # Retrieve API Key to use as session token
            # Note: In a future improved design, we should use a separate session token or JWT.
            # For now, reusing API Key as the token to maintain compatibility with require_api_key dependency.
            token = await AuthService.get_decrypted_api_key(int(user["user_id"]))
            if not token:
                # Should not happen because API Key is required in DB schema
                 raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="User has no API Key"
                )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must provide api_key OR username/password"
        )
            
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Set HttpOnly cookie for docs access
    if token:
        response.set_cookie(
            key="admin_token",
            value=token,
            httponly=True,
            max_age=86400, # 24 hours
            samesite="lax",
            secure=False # Set to True in production with HTTPS
        )
        # Return MASKED API key to client to encourage Cookie usage while maintaining basic visibility
        if len(token) > 10:
            user["api_key"] = f"{token[:4]}...{token[-2:]}"
        else:
            user["api_key"] = "***"
    
    return {
        "status": "success",
        "data": user
    }

@router.post("/sso/login", summary="SSO 登录")
async def sso_login(request: SSOLoginRequest, response: Response):
    """
    SSO 登录接口
    
    通过 Yovole SSO 系统进行认证，验证成功后查询本地用户信息。
    
    **请求参数：**
    - **username**: 用户名
    - **password**: 密码
    
    **响应示例：**
    ```json
    {
      "status": "success",
      "data": {
        "user_id": "1",
        "user_name": "admin",
        "role": "admin"
      }
    }
    ```
    
    **错误响应：**
    - `401 Unauthorized`: SSO 认证失败或用户不存在/被禁用
    - `503 Service Unavailable`: SSO 服务不可用
    """
    user = await AuthService.authenticate_sso_user(request.username, request.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="SSO authentication failed"
        )
    
    # 检查是否有错误信息
    if user.get("error") == "user_not_found":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="请联系管理员开通"
        )
    
    if user.get("error") == "user_disabled":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户已被禁用"
        )
    
    # 获取用户的 API Key
    token = await AuthService.get_decrypted_api_key(int(user["user_id"]))
    if not token:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User has no API Key"
        )
    
    # Set HttpOnly cookie for docs access
    response.set_cookie(
        key="admin_token",
        value=token,
        httponly=True,
        max_age=86400, # 24 hours
        samesite="lax",
        secure=False # Set to True in production with HTTPS
    )
    # Return MASKED API key to client to encourage Cookie usage while maintaining basic visibility
    if len(token) > 10:
        user["api_key"] = f"{token[:4]}...{token[-2:]}"
    else:
        user["api_key"] = "***"
    
    return {
        "status": "success",
        "data": user
    }

@router.post("/logout", summary="退出登录")
async def logout(
    response: Response,
    api_key: Optional[str] = Header(None, alias="X-API-Key")
):
    """
    退出登录并清除 Cookie 和 Redis 缓存
    """
    if api_key:
        await AuthService.expire_api_key(api_key)
        
    response.delete_cookie(key="admin_token")
    return {"status": "success", "message": "Logged out successfully"}



@router.get("/me", summary="获取当前用户信息")
async def get_current_user_info(
    user: dict = Depends(require_api_key)
):
    """
    获取当前认证用户的详细信息
    
    用于验证 API Key 的有效性并获取用户详情，前端可用此接口验证登录状态。
    
    **请求头：**
    - **X-API-Key**: 用户的 API 密钥
    
    **响应示例：**
    ```json
    {
      "id": "1",
      "user_id": "1",
      "user_name": "admin",
      "role": "admin",
      "created_at": "2025-01-01 12:00:00",
      "remark": "管理员账户",
      "status": "active"
    }
    ```
    
    **错误响应：**
    - `401 Unauthorized`: API Key 无效或已过期
    """
    return {
        "status": "success",
        "data": {
            "id": user.get("user_id"),
            "user_id": user.get("user_id"),
            "user_name": user.get("user_name"),
            "role": user.get("role"),
            "created_at": user.get("created_at"),
            "remark": user.get("remark"),
            "status": "active"
        }
    }
