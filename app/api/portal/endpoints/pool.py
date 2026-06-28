from fastapi import APIRouter, Depends
from app.services.pool_manager import DataSourcePoolManager
from app.core.dependencies import require_admin

router = APIRouter()

@router.get("/status", summary="获取连接池状态")
async def get_pool_status(source_id: int):
    """
    获取指定数据源的连接池状态
    """
    return await DataSourcePoolManager.get_pool_status(source_id)

@router.post("/health/check", summary="执行连接池健康检查")
async def check_pools_health():
    """
    触发所有活跃连接池的健康检查 (Ping)
    """
    return await DataSourcePoolManager.check_health()
