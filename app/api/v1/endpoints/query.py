from fastapi import APIRouter, Depends, HTTPException, Body, Response
from typing import List, Any, Optional, Union
from pydantic import BaseModel, Field
from app.services.data_adapter import get_adapter, LogicalQuery
from app.api.v1.schemas.data import DataPageResponse, PageData
from app.core.dependencies import require_api_key, verify_resource_access, check_rate_limit
from app.services.meta_service import MetaService
from app.core import redis
import hashlib
import json
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Schema Definition
class LogicalQueryRequest(BaseModel):
    resource: str = Field(
        ..., 
        description="目标数据资源名称。可选值：-请查看 `右上角` 的 `我的权限` 里面的描述",
        example="donghuan_real_metrics"
    )
    filters: List[Union[List[Any], Any]] = Field(
        default=[], 
        description="""
筛选条件列表。每个条件为一个三元组列表：`[字段名, 操作符, 值]`。
支持的操作符：`=`, `!=`, `>`, `<`, `>=`, `<=`, `LIKE`, `IN`。
例如：`[["metric_value", ">", "30"], ["resource_id", "IN", ["R001", "R002"]]]`
        """,
        example=[["metric_value", ">", "30"], ["resource_id", "=", "R001"]]
    )
    sort_by: Optional[str] = Field(
        "metric_time",
        description="排序字段名。默认按时间排序。",
        example="metric_time"
    )
    sort_order: Optional[str] = Field(
        "desc",
        description="排序方向：`asc` (升序) 或 `desc` (降序)",
        example="desc"
    )
    page: int = Field(
        1, 
        ge=1,
        description="页码，从 1 开始",
        example=1
    )
    size: int = Field(
        20, 
        ge=1, 
        le=1000,
        description="每页条数，最大 1000",
        example=20
    )

@router.post("/", response_model=DataPageResponse, summary="通用逻辑查询")
async def execute_query(
    query_in: LogicalQueryRequest,
    response: Response,
    user: dict = Depends(require_api_key),
    _rate_limit: None = Depends(check_rate_limit)
):
    """
    执行通用逻辑查询
    
    提供灵活的逻辑查询能力，无需编写 SQL，通过声明式的条件筛选即可查询数据。
    
    **支持的资源：**
    - 请查看 `右上角` 的 `我的权限` 里面的描述
    
    **筛选操作符：**
    - `=`: 等于
    - `!=`: 不等于
    - `>`: 大于
    - `<`: 小于
    - `>=`: 大于等于
    - `<=`: 小于等于
    - `LIKE`: 模糊匹配
    - `IN`: 在列表中
    
    **请求示例：**
    ```json
    {
      "resource": "donghuan_real_metrics",
      "filters": [
        ["metric_value", ">", "30"],
        ["resource_id", "=", "R001"]
      ],
      "sort_by": "metric_time",
      "sort_order": "desc",
      "page": 1,
      "size": 20
    }
    ```
    
    **响应示例：**
    ```json
    {
      "code": 200,
      "message": "success",
      "data": {
        "items": [...],
        "total": 100,
        "page": 1,
        "size": 20,
        "pages": 5
      }
    }
    ```
    
    **错误响应：**
    - `400 Bad Request`: 资源名称无效或筛选条件格式错误
    - `401 Unauthorized`: API Key 无效
    - `429 Too Many Requests`: 超出限流阈值
    - `500 Internal Server Error`: 服务器内部错误
    """
    try:
        # Check permission for the requested resource
        await verify_resource_access(user, query_in.resource)

        # Get resource config to determine data source
        resource_config = await MetaService.get_config(query_in.resource)
        if not resource_config:
            raise HTTPException(status_code=404, detail=f"Resource not found: {query_in.resource}")

        # --- Cache Logic Start ---
        cache_key = None
        if resource_config.cache_ttl and resource_config.cache_ttl > 0:
            try:
                # Create a stable cache key based on query parameters
                query_dict = query_in.dict()
                query_str = json.dumps(query_dict, sort_keys=True)
                query_hash = hashlib.md5(query_str.encode()).hexdigest()
                cache_key = f"nanzi:query:{query_in.resource}:{query_hash}"
                
                r = await redis.get_redis()
                if r:
                    cached_data = await r.get(cache_key)
                    if cached_data:
                        logger.info(f"⚡ Cache HIT for {cache_key}")
                        response.headers["X-Cache"] = "HIT"
                        # Deserialize and return
                        data_dict = json.loads(cached_data)
                        return DataPageResponse(**data_dict)
            except Exception as e:
                logger.warning(f"Cache read error: {e}")

        response.headers["X-Cache"] = "MISS"
        # --- Cache Logic End ---

        adapter = await get_adapter(resource_config.data_source)
        
        # Convert Pydantic model to Data Class
        # filters is list of lists, need to be list of tuples for adapter if it expects tuples, 
        # checking adapter code: `for i, (f, op, v) in enumerate(query.filters):` -> unpacks 3 items.
        # So list of lists is fine as long as they have 3 elements.
        
        internal_filters = []
        for f in query_in.filters:
            if isinstance(f, list) and len(f) == 3:
                internal_filters.append(tuple(f))
            else:
                 # Initial validation strictly expects [field, op, value]
                 raise ValueError("Each filter must be a list of 3 elements: [field, op, value]")

        logical_query = LogicalQuery(
            resource=query_in.resource,
            filters=internal_filters,
            sort_by=query_in.sort_by,
            sort_order=query_in.sort_order,
            page=query_in.page,
            size=query_in.size
        )
        
        result = await adapter.execute(logical_query)
        
        # Result is ResultSet(items, total, page, size, pages)
        # DataPageResponse expects data=PageData(...)
        
        resp_data = DataPageResponse(
            data=PageData(
                items=result.items,
                total=result.total,
                page=result.page,
                size=result.size,
                pages=result.pages
            )
        )

        # --- Cache Write Start ---
        if cache_key and resource_config.cache_ttl > 0:
            try:
                r = await redis.get_redis()
                if r:
                    # Use Pydantic's json() or dict() to serialize
                    # handling datetime might be needed if not handled by json.dumps default
                    # resp_data.json() returns string
                    await r.setex(
                        cache_key,
                        resource_config.cache_ttl,
                        resp_data.json()
                    )
            except Exception as e:
                logger.warning(f"Cache write error: {e}")
        # --- Cache Write End ---

        return resp_data

    except ValueError as e:
        # Catch validaton errors (like unknown resource or invalid filters) from Adapter
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
