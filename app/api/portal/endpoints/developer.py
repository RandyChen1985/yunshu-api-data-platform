from fastapi import APIRouter, Depends
from typing import List, Dict
from app.core.errors import ErrorCode, ERROR_CODE_DESC
from app.core.dependencies import require_api_key

router = APIRouter()

@router.get("/error-codes")
async def get_error_codes(user: dict = Depends(require_api_key)):
    """获取系统定义的业务错误码字典"""
    codes = []
    for code in ErrorCode:
        codes.append({
            "code": int(code),
            "name": code.name,
            "description": ERROR_CODE_DESC.get(code, "未知错误")
        })
    return sorted(codes, key=lambda x: x["code"])

@router.get("/sdk-metadata")
async def get_sdk_metadata(user: dict = Depends(require_api_key)):
    """获取用于生成 SDK 的元数据（例如当前用户的 API Key 占位符）"""
    return {
        "user_name": user.get("user_name"),
        "role": user.get("role"),
        "default_api_key": "YOUR_API_KEY_HERE" # 安全起见，不直接返回明文 Key
    }
