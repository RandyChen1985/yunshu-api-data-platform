from fastapi import APIRouter, Depends
from app.core.dependencies import require_admin, require_api_key
from app.api.portal.endpoints import auth, audit, management, keys, dashboard, system, meta, datasource

portal_router = APIRouter()

# 1. 认证路由 (登录/退出)
portal_router.include_router(auth.router, prefix="/auth", tags=["认证"])

# 2. 用户管理路由 (统一管理)
# 注意：该路由内部已自行处理 admin 和 user 的权限区分
portal_router.include_router(management.router, prefix="/management", tags=["用户管理"])

# 3. 密钥管理路由 (仅限管理员)
# 在此处应用 require_admin 依赖
portal_router.include_router(keys.router, prefix="/keys", tags=["密钥管理"], dependencies=[Depends(require_admin)])

# 4. 系统配置路由 (内部控制权限)
portal_router.include_router(system.router, prefix="/system", tags=["系统配置"])

# 5. 审计与仪表板 (需要登录)
portal_router.include_router(audit.router, prefix="/audit", tags=["审计日志"], dependencies=[Depends(require_api_key)])
portal_router.include_router(dashboard.router, prefix="/dashboard", tags=["仪表板"], dependencies=[Depends(require_api_key)])

# 6. 数据源管理路由 (读写权限在内部控制)
portal_router.include_router(datasource.router, prefix="/datasource", tags=["数据源管理"])

# 7. 元数据管理路由 (读写权限在内部控制)
portal_router.include_router(meta.router, prefix="/meta", tags=["元数据管理"])

# 7.1 语义化元数据管理 (V2)
from app.api.portal.endpoints import meta_v2
portal_router.include_router(meta_v2.router, prefix="/meta/v2", tags=["语义元数据"])

# 8. 连接池监控 (仅限管理员)
from app.api.portal.endpoints import pool
portal_router.include_router(pool.router, prefix="/pool", tags=["连接池管理"], dependencies=[Depends(require_admin)])

# 9. 访问日志 (允许登录用户访问，内部逻辑处理权限)
from app.api.portal.endpoints import logs
portal_router.include_router(logs.router, prefix="/logs", tags=["访问日志"], dependencies=[Depends(require_api_key)])

# 10. SQL 实验室 (内部控制权限)
from app.api.portal.endpoints import lab, developer, masking
portal_router.include_router(lab.router, prefix="/lab", tags=["SQL实验室"])

# 11. 系统资源监控 (仅限管理员)
from app.api.portal.endpoints import monitor
portal_router.include_router(monitor.router, prefix="/monitor", tags=["系统监控"], dependencies=[Depends(require_admin)])

# 12. 开发者门户 (元数据/SDK/错误码)
portal_router.include_router(developer.router, prefix="/developer", tags=["开发者中心"], dependencies=[Depends(require_api_key)])

# 13. 数据脱敏管理 (仅限管理员)
portal_router.include_router(masking.router, prefix="/system/masking", tags=["数据脱敏"], dependencies=[Depends(require_admin)])

# 14. 数据产品目录与资产全景
from app.api.portal.endpoints import catalog
portal_router.include_router(catalog.router, prefix="/catalog", tags=["数据产品目录"], dependencies=[Depends(require_api_key)])