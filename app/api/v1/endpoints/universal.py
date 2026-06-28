from fastapi import APIRouter, Depends, Query, Request, HTTPException
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from app.core.dependencies import require_api_key, verify_resource_access, check_rate_limit
from app.services.data_adapter.models import LogicalQuery, ResultSet
from app.services.data_adapter.factory import get_adapter
from app.api.v1.schemas.data import BaseResponse
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/resources/{resource_key}", response_model=BaseResponse, include_in_schema=False)
async def get_resource_data(
    resource_key: str,
    request: Request,
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=1000, description="Page size"),
    sort_by: Optional[str] = Query(None, description="Sort field"),
    sort_order: str = Query("DESC", pattern="^(ASC|DESC)$", description="Sort order"),
    unmask: bool = Query(False, description="Whether to unmask data (Admin only)"),
    user: Dict = Depends(require_api_key),
    _rate_limit: None = Depends(check_rate_limit)
):
    """
    Universal endpoint to access dynamic resources.
    
    **Filter Usage / 筛选规则:**
    Any query parameters other than `page`, `size`, `sort_by`, `sort_order` will be treated as filters.
    
    **1. Single Value (Equality) / 单值精确匹配:**
    Format: `key=value`
    Example: `?status=active`  =>  `WHERE status = 'active'`
    
    **2. Multiple Values (IN Query) / 多值包含查询:**
    Supports two formats:
    
    *   **Repeated Keys / 重复参数名:**
        Format: `key=value1&key=value2`
        Example: `?city=Beijing&city=Shanghai`  =>  `WHERE city IN ('Beijing', 'Shanghai')`
        
    *   **JSON Array String / JSON 数组字符串 (Recommended for Arrays):**
        Format: `key=["value1", "value2"]`
        Example: `?city=["Beijing", "Shanghai"]`  =>  `WHERE city IN ('Beijing', 'Shanghai')`
        
    **Note:**
    - If a JSON array string is invalid, it will be treated as a literal string value.
    - Mixed usage is supported (e.g. `key=["A"]&key=B` => `IN ('A', 'B')`).
    """
    # 1. Permission Check
    await verify_resource_access(user, resource_key)

    # 2. Parse Dynamic Filters from Query Params
    reserved_params = {"page", "size", "sort_by", "sort_order", "unmask"}
    filters = []
    
    # Collect logic: handle multiple values for same key as IN check
    raw_params = {} # key -> list of values
    for k, v in request.query_params.multi_items():
        if k in reserved_params:
            continue
        if k not in raw_params:
            raw_params[k] = []
        raw_params[k].append(v)
        
    import json
    for k, values in raw_params.items():
        final_values = []
        
        # Check if we need to parse JSON strings from the values
        # e.g. city=["Beijing", "Shanghai"]
        for val in values:
            parsed = False
            if isinstance(val, str) and val.strip().startswith('[') and val.strip().endswith(']'):
                try:
                    loaded_val = json.loads(val)
                    if isinstance(loaded_val, list):
                        final_values.extend(loaded_val)
                        parsed = True
                except (json.JSONDecodeError, TypeError):
                    pass
            
            if not parsed:
                final_values.append(val)

        if len(final_values) > 1:
            filters.append((k, "IN", final_values))
        elif len(final_values) == 1:
            filters.append((k, "=", final_values[0]))

    # 3. Construct Logical Query
    query = LogicalQuery(
        resource=resource_key,
        page=page,
        size=size,
        filters=filters,
        sort_by=sort_by,
        sort_order=sort_order
    )

    # 4. Execute via Adapter
    from app.services.meta_service import MetaService
    config = await MetaService.get_config(resource_key)
    if not config:
        raise HTTPException(status_code=404, detail=f"Resource {resource_key} not found")
        
    adapter = await get_adapter(config.data_source)
    result = await adapter.execute(query)
    
    # 5. Apply Data Masking
    from app.services.masking_service import MaskingService
    if await MaskingService.should_mask(user, unmask):
        result.items = await MaskingService.mask_recursive(result.items)
    
    return BaseResponse(
        data=result,
        message="Success"
    )

# --- POST Support ---

class ResourceQueryRequest(BaseModel):
    filters: List[Union[List[Any], Any]] = Field(
        default=[], 
        description="筛选条件列表。与 /api/v1/query 格式一致：[[field, op, value], ...]",
        example=[["status", "=", "active"]]
    )
    page: int = Field(1, ge=1, description="页码")
    size: int = Field(20, ge=1, le=1000, description="每页大小")
    sort_by: Optional[str] = Field(None, description="排序字段")
    sort_order: str = Field("desc", pattern="^(asc|desc|ASC|DESC)$", description="排序方向")
    unmask: bool = Field(False, description="是否脱敏 (Admin only)")

@router.post("/resources/{resource_key}", response_model=BaseResponse, summary="动态资源查询 (POST)", include_in_schema=False)
async def query_resource_data(
    resource_key: str,
    query_in: ResourceQueryRequest,
    user: Dict = Depends(require_api_key),
    _rate_limit: None = Depends(check_rate_limit)
):
    """
    Universal endpoint to access dynamic resources via POST.
    Allows complex filters (like large arrays) that are difficult to pass in URL.
    """
    # 1. Permission Check
    await verify_resource_access(user, resource_key)

    # 2. Parse Filters
    # Re-use logic from query.py or similar: ensure list of tuples
    internal_filters = []
    for f in query_in.filters:
        if isinstance(f, list) and len(f) == 3:
            internal_filters.append(tuple(f))
        else:
             raise HTTPException(status_code=400, detail="Each filter must be a list of 3 elements: [field, op, value]")

    # 3. Construct Logical Query
    query = LogicalQuery(
        resource=resource_key,
        page=query_in.page,
        size=query_in.size,
        filters=internal_filters,
        sort_by=query_in.sort_by,
        sort_order=query_in.sort_order
    )

    # 4. Execute via Adapter
    from app.services.meta_service import MetaService
    config = await MetaService.get_config(resource_key)
    if not config:
        raise HTTPException(status_code=404, detail=f"Resource {resource_key} not found")
        
    adapter = await get_adapter(config.data_source)
    result = await adapter.execute(query)
    
    # 5. Apply Data Masking
    from app.services.masking_service import MaskingService
    if await MaskingService.should_mask(user, query_in.unmask):
        result.items = await MaskingService.mask_recursive(result.items)
    
    return BaseResponse(
        data=result,
        message="Success"
    )
