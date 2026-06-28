from fastapi import APIRouter, Depends
from app.services.monitor_service import MonitorService
from app.core.dependencies import require_admin

router = APIRouter()

@router.get("/server", summary="获取服务器资源监控")
async def get_server_stats(user: dict = Depends(require_admin)):
    return MonitorService.get_server_stats()

@router.get("/redis", summary="获取Redis监控")
async def get_redis_stats(user: dict = Depends(require_admin)):
    return await MonitorService.get_redis_stats()
