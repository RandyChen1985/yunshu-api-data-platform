# 云枢・智维・AI 平台 - API服务化详细设计文档

## 1. 文档信息

- **文档名称**：API服务化详细设计文档
- **系统名称**：云枢・数据服务平台（Yunshu Data API Platform）
- **所属项目**：云枢・智维・AI
- **版本**：v1.0
- **日期**：2025-12-25
- **作者**：开发团队

## 2. 模块详细设计

### 2.1 API服务模块

#### 2.1.1 主应用入口 (main.py)

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.endpoints import resources, query, keys, monitor
from app.core.config import settings
from app.core.exceptions import setup_exception_handlers

app = FastAPI(
    title="云枢・智维・AI API服务",
    description="数据中心智能运营管理平台API服务",
    version="1.0.0",
    openapi_url="/api/v1/openapi.json"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册异常处理器
setup_exception_handlers(app)

# 注册路由
app.include_router(resources.router, prefix="/api/v1/resources", tags=["resources"])
app.include_router(query.router, prefix="/api/v1/query", tags=["query"])
app.include_router(keys.router, prefix="/api/v1/keys", tags=["keys"])
app.include_router(monitor.router, prefix="/api/v1/monitor", tags=["monitor"])

@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    from app.core.database import init_db
    await init_db()

@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    from app.core.database import close_db
    await close_db()
```

#### 2.1.2 资源化 API 端点 (api/v1/endpoints/resources.py)

```python
from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Optional, List
from app.api.v1.schemas.data import (
    DataQueryParams,
    DataPageResponse,
    DonghuanRealMetricResponse
)
from app.services.data_service import DataService
from app.core.security import require_api_key

router = APIRouter()

@router.get("/donghuan/real-metrics", response_model=DataPageResponse[DonghuanRealMetricResponse])
async def list_donghuan_real_metrics(
    params: DataQueryParams = Depends(),
    current_user: dict = Depends(require_api_key)
):
    """动环实时指标（示例）"""
    try:
        result = await DataService.list_donghuan_real_metrics(params)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

#### 2.1.3 数据模型定义 (api/v1/schemas/data.py)

```python
from pydantic import BaseModel
from typing import Optional, List, Generic, TypeVar
from datetime import datetime

T = TypeVar('T')

class BaseResponse(BaseModel):
    """基础响应模型，统一 Envelope 结构 { code, message, data, timestamp, trace_id } 的公共部分"""
    code: int = 200
    message: str = "success"
    timestamp: Optional[datetime] = None
    trace_id: Optional[str] = None

class DataQueryParams(BaseModel):
    """数据查询参数（资源化接口与通用查询接口可复用，MVP 先覆盖常用字段）"""
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    resource_id: Optional[str] = None
    metric_name: Optional[str] = None
    page: int = 1
    size: int = 20
    sort_by: Optional[str] = None
    sort_order: Optional[str] = "desc"

class DonghuanRealMetricResponse(BaseModel):
    """动环实时指标响应（ck_fact_donghuan_real_metric_hbase）"""
    rowkey: str
    c_datacenter_id: Optional[str] = None
    resource_id: Optional[str] = None
    metric_name: Optional[str] = None
    metric_value: Optional[str] = None
    metric_unit: Optional[str] = None
    metric_time: str
    status: Optional[str] = None

class PageData(BaseModel, Generic[T]):
    """分页数据体，作为 Envelope.data 的固定结构"""
    items: List[T]
    total: int
    page: int
    size: int
    pages: int

class DataPageResponse(BaseResponse, Generic[T]):
    """分页数据响应，继承统一 Envelope 字段"""
    data: PageData[T]
```

### 2.2 鉴权与 API Key 模块

#### 2.2.1 API Key 服务 (services/auth_service.py)

```python
import hashlib
import secrets
from typing import Optional, Dict
from app.core.config import settings
from app.core.database import get_db_connection

class AuthService:
    @staticmethod
    async def generate_api_key(user_name: str) -> str:
        """生成API密钥"""
        api_key = secrets.token_urlsafe(32)
        hashed_key = hashlib.sha256(api_key.encode()).hexdigest()
      
        # 存储到数据库
        conn = await get_db_connection()
        await conn.execute(
            "INSERT INTO api_users (user_name, api_key, permissions, status) VALUES (?, ?, ?, ?)",
            (user_name, hashed_key, '{"access": ["read"]}', 1)
        )
      
        return api_key

    @staticmethod
    async def verify_api_key(api_key: str) -> Optional[Dict]:
        """校验 API Key（对比哈希）"""
        hashed_key = hashlib.sha256(api_key.encode()).hexdigest()
        conn = await get_db_connection()
        result = await conn.fetchrow(
            "SELECT id, user_name, permissions, status FROM api_users WHERE api_key = ?",
            (hashed_key,)
        )
        if not result or result.get('status') != 1:
            return None
        return {
            "user_id": result.get('id'),
            "user_name": result.get('user_name'),
            "permissions": result.get('permissions')
        }

    @staticmethod
    async def get_user_permissions(user_id: int) -> Dict:
        """获取用户权限"""
        conn = await get_db_connection()
        result = await conn.fetchrow(
            "SELECT permissions FROM api_users WHERE id = ? AND status = 1",
            (user_id,)
        )
        if result:
            return result['permissions']
        return {}
```

#### 2.2.2 安全依赖 (core/security.py)

```python
from fastapi import Depends, HTTPException, Header, status
from typing import Dict, Optional
from app.services.auth_service import AuthService

async def require_api_key(
    api_key: Optional[str] = Header(default=None, alias="X-API-Key"),
    scopes: Optional[str] = Header(default=None, alias="X-Scopes"),
) -> Dict:
    """校验 API Key。
 
    说明：`X-Scopes` 为上游透传字段，MVP 阶段不做强校验，仅用于日志审计与后续扩展预留。
    """
    if not api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing X-API-Key")
    info = await AuthService.verify_api_key(api_key)
    if not info:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")
    info["scopes"] = scopes
    return info
```

### 2.3 数据访问服务

#### 2.3.1 数据服务 (services/data_service.py)

```python
from typing import List, Dict, Optional, Any
from datetime import datetime
from app.api.v1.schemas.data import DataQueryParams, DonghuanRealMetricResponse, DataPageResponse, PageData
from app.core.database import get_clickhouse_connection
from app.core.cache import get_cache, set_cache
import json

class DataSourceAdapter:
    """数据源适配抽象"""
    async def execute(self, query: "LogicalQuery") -> "ResultSet":
        raise NotImplementedError

class ClickHouseAdapter(DataSourceAdapter):
    """ClickHouse 适配实现"""
    async def execute(self, query: "LogicalQuery") -> "ResultSet":
        # 1. 转换 LogicalQuery -> ClickHouse SQL
        # 2. 执行查询 (使用 aiochclient 或 asynch)
        # 3. 封装结果为 ResultSet
        pass

class DataService:
    """数据服务层示例。
 
    说明：本示例直接使用 ClickHouse 表 `ck_fact_donghuan_real_metric_hbase`（见 `architech/db-schemal/CLICKHOUSE_TABLES.md`），实际实现中应通过 `QueryEngine + DataSourceAdapter`
    构造标准化逻辑查询（维度、指标、过滤、聚合等），并在执行前统一注入用户角色与数据资源范围（regions/rooms 等）
    的权限过滤条件，从而支持 ClickHouse / HBase / MySQL 等多数据源并保证安全边界。
    """

    @staticmethod
    async def list_donghuan_real_metrics(params: DataQueryParams) -> DataPageResponse[DonghuanRealMetricResponse]:
        """查询动环实时指标 (Refactored to use Adapter & prevent Injection)"""
        
        # 1. 构造标准逻辑查询对象 (LogicalQuery)
        # 实际代码中应由 QueryBuilder 统一处理
        query = LogicalQuery(
            resource="donghuan_real_metrics",
            filters=[],
            sort_by=params.sort_by,
            sort_order=params.sort_order,
            page=params.page,
            size=params.size
        )

        # 2. 注入过滤条件
        if params.start_time:
            query.add_filter("metric_time", ">=", params.start_time)
        if params.end_time:
            query.add_filter("metric_time", "<=", params.end_time)
        if params.resource_id:
            query.add_filter("resource_id", "=", params.resource_id)

        # 3. 校验排序字段防注入 (Security Fix)
        ALLOWED_SORTS = {'metric_time', 'metric_value', 'resource_id'}
        if query.sort_by and query.sort_by not in ALLOWED_SORTS:
             query.sort_by = 'metric_time' # Fallback or Raise Error

        # 4. 获取适配器并执行
        # 在实际应用中，adapter 应通过依赖注入或工厂获取
        adapter = get_adapter(DataSourceType.CLICKHOUSE) 
        result_set = await adapter.execute(query)

        return DataPageResponse(
            data=PageData(
                items=result_set.items,
                total=result_set.total,
                page=params.page,
                size=params.size,
                pages=result_set.pages
            )
        )

    @staticmethod
    async def get_temperature_summary(
        start_time: str, 
        end_time: str, 
        resource_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """获取温度数据汇总"""
        # 尝试从缓存获取
        cache_key = f"temp_summary_{start_time}_{end_time}_{resource_id or 'all'}"
        cached_result = await get_cache(cache_key)
        if cached_result:
            return json.loads(cached_result)
      
        # 构建查询
        where_clause = ["metric_time >= ?", "metric_time <= ?"]
        params_list = [start_time, end_time]
      
        if resource_id:
            where_clause.append("resource_id = ?")
            params_list.append(resource_id)
      
        where_str = " AND ".join(where_clause)
      
        conn = await get_clickhouse_connection()
        result = await conn.fetchrow(f"""
            SELECT 
                AVG(metric_value) as avg_temp,
                MIN(metric_value) as min_temp,
                MAX(metric_value) as max_temp,
                COUNT(*) as count
            FROM ck_fact_donghuan_real_metric_hbase 
            WHERE {where_str}
        """, *params_list)
      
        summary = {
            "average_temperature": float(result['avg_temp']) if result['avg_temp'] else 0,
            "min_temperature": float(result['min_temp']) if result['min_temp'] else 0,
            "max_temperature": float(result['max_temp']) if result['max_temp'] else 0,
            "count": result['count'] or 0,
            "time_range": {
                "start_time": start_time,
                "end_time": end_time
            }
        }
      
        # 缓存结果（1小时）
        await set_cache(cache_key, json.dumps(summary), expire=3600)
      
        return summary
```

## 3. API接口详细设计

### 3.1 动环实时指标 API

#### 3.1.1 查询动环实时指标

- **接口路径**: `GET /api/v1/resources/donghuan/real-metrics`
- **请求参数**:
  - `start_time`: 开始时间 (可选)
  - `end_time`: 结束时间 (可选)
  - `resource_id`: 资源ID (可选)
  - `metric_name`: 指标名称 (可选)
  - `page`: 页码 (可选, 默认1)
  - `size`: 每页数量 (可选, 默认20)
  - `sort_by`: 排序字段 (可选)
  - `sort_order`: 排序方向 (可选, 默认desc)
- **响应示例**:

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "items": [],
    "total": 0,
    "page": 1,
    "size": 20,
    "pages": 0
  },
  "timestamp": "2025-12-26T11:00:00+08:00",
  "trace_id": "..."
}
```

#### 3.1.2 获取动环实时指标汇总

- **接口路径**: `GET /api/v1/resources/donghuan/real-metrics/summary`
- **请求参数**:
  - `start_time`: 开始时间 (必填)
  - `end_time`: 结束时间 (必填)
  - `resource_id`: 资源ID (可选)
- **响应示例**:

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "average_temperature": 24.5,
    "min_temperature": 22.1,
    "max_temperature": 28.3,
    "count": 1000,
    "time_range": {
      "start_time": "2025-12-25T00:00:00",
      "end_time": "2025-12-25T23:59:59"
    }
  },
  "timestamp": "2025-12-26T11:00:00+08:00",
  "trace_id": "..."
}
```

### 3.2 API Key 管理 API

#### 3.2.1 创建 API Key

- **接口路径**: `POST /api/v1/keys`
- **请求参数**:
  - `user_name`: 用户名
- **说明**: MVP 阶段该接口可用于初始化/发放 API Key，可按部署环境决定是否需要额外保护（如内网访问、IP 白名单或管理口令）
- **响应示例**:

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "api_key": "sk-1234567890abcdef",
    "key_id": 1
  },
  "timestamp": "2025-12-26T11:00:00+08:00",
  "trace_id": "..."
}
```

### 3.3 统一响应格式与错误码

系统通过全局异常处理器（Global Exception Handler）确保所有 API 响应（包括错误响应）遵循统一的 Envelope 结构。

#### 3.3.1 响应结构

```json
{
  "code": 200,
  "message": "success",
  "data": { ... },
  "timestamp": "2025-01-01T12:00:00.000000",
  "trace_id": "req-uuid-..."
}
```

#### 3.3.2 业务错误码表

| 状态码 | 业务码 | 含义 | 说明 |
| :--- | :--- | :--- | :--- |
| 200 | 200 | 成功 | 请求处理成功 |
| 400 | 400 | 参数错误 | 请求参数校验失败或资源名称无效 |
| 401 | 401 | 认证失败 | API Key 缺失、无效或已过期 |
| 403 | 403 | 权限不足 | 用户角色权限不足，或未被授权访问特定资源 |
| 429 | 429 | 请求过多 | 触发限流策略（普通用户 100/min，管理员 1000/min） |
| 500 | 500 | 系统错误 | 服务器内部未知错误 |
| 503 | 503 | 服务不可用 | 数据库（MySQL/ClickHouse）连接失败，建议 30s 后重试 |

### 3.4 基于资源的权限控制

为了保证数据安全，系统实现了细粒度的资源访问控制。

#### 3.4.1 角色模型
- **admin**: 管理员角色，拥有系统全量权限，可访问所有 API 且不受资源授权限制。
- **user**: 普通用户角色，默认无权访问任何数据资源，必须经过显式授权。

#### 3.4.2 资源授权机制
在 `api_users` 表的 `permissions` 字段中存储授权信息：
```json
{
  "allowed_resources": [
    "donghuan_real_metrics",
    "donghuan_events",
    "yunshu_rooms"
  ]
}
```
当普通用户请求接口时，系统会校验请求的目标资源是否在上述列表中。

---

## 7. 测试用例设计

### 7.1 单元测试

```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_get_donghuan_real_metrics():
    """测试查询动环实时指标（资源化接口）"""
    response = client.get(
        "/api/v1/resources/donghuan/real-metrics",
        headers={"X-API-Key": "test"}
    )
    assert response.status_code == 200
    assert "data" in response.json()

def test_get_donghuan_real_metrics_summary():
    """测试查询动环实时指标汇总"""
    import datetime
    start_time = datetime.datetime.now().isoformat()
    end_time = datetime.datetime.now().isoformat()
  
    response = client.get(
        f"/api/v1/resources/donghuan/real-metrics/summary?start_time={start_time}&end_time={end_time}",
        headers={"X-API-Key": "test"}
    )
    assert response.status_code == 200
    assert "average_temperature" in response.json()

def test_auth_generate_key():
    """测试创建 API Key"""
    response = client.post(
        "/api/v1/keys",
        json={"user_name": "test_user"}
    )
    assert response.status_code == 200
    assert "api_key" in response.json()
```

## 8. 部署配置

### 8.1 Dockerfile

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制代码
COPY . .

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### 8.2 Docker Compose (docker-compose.yml)

```yaml
version: '3.8'

services:
  api-service:
    build: .
    ports:
      - "8000:8000"
    environment:
      - CLICKHOUSE_HOST=clickhouse
      - REDIS_HOST=redis
    depends_on:
      - clickhouse
      - redis
    restart: unless-stopped

  clickhouse:
    image: clickhouse/clickhouse-server:latest
    ports:
      - "9000:9000"
      - "8123:8123"
    volumes:
      - clickhouse_data:/var/lib/clickhouse
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

volumes:
  clickhouse_data:
  redis_data:
```

## 9. 性能优化策略

### 9.1 数据库优化

- 合理使用索引
- 查询语句优化
- 分区表设计
- 预聚合表

### 9.2 缓存策略

- 热点数据缓存
- 查询结果缓存
- 分布式缓存
- 缓存预热

### 9.3 连接池优化

- 数据库连接池
- 连接复用
- 连接监控
- 自动扩缩容
