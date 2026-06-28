from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Optional, List, Dict
from pydantic import BaseModel, Field
from app.services.metadata_v2_service import MetadataV2Service
from app.services.metadata_yaml_service import MetadataYamlService
from app.core.dependencies import require_api_key
from app.services.permission_service import PermissionService

router = APIRouter()

# 资源权限 Key
RESOURCE_PERMISSION = "system.metadata.search"

class SearchRequest(BaseModel):
    query: str = Field(..., description="检索关键词或自然语言问题")
    data_source: str = Field("default", description="目标数据源编码")
    search_type: str = Field("keyword", description="检索模式：keyword (模糊匹配) | semantic (语义检索)")
    enable_rerank: bool = Field(False, description="是否启用 Rerank 重排序 (仅语义检索有效)")

class ExternalSearchResponse(BaseModel):
    data: str = Field(..., description="装配后的 YAML 上下文")
    count: int = Field(..., description="涉及的数据集数量")
    dataset_ids: List[int] = Field(..., description="涉及的数据集 ID 列表")

async def _verify_resource_permission(user: Dict = Depends(require_api_key)):
    """校验外部用户是否拥有调用元数据检索资源的权限"""
    if user.get("role") == "admin":
        return user
        
    user_id = int(user["user_id"])
    user_perms = await PermissionService.get_user_permissions(user_id)
    
    if RESOURCE_PERMISSION not in user_perms.permissions.resources:
        raise HTTPException(
            status_code=403, 
            detail=f"Permission Denied: Missing resource access for {RESOURCE_PERMISSION}"
        )
    return user

@router.post("/search", response_model=ExternalSearchResponse)
async def external_search_metadata(
    request: SearchRequest, 
    user=Depends(_verify_resource_permission)
):
    """
    对外开放的语义元数据检索接口 (V1)
    
    支持多策略召回：
    - **keyword**: 基于关键词的数据库模糊匹配。
    - **semantic**: 基于向量库的语义检索，支持可选的 Rerank 精排。
    
    必须在“资源管理”中为角色分配 system.metadata.search 权限方可调用。
    """
    if not request.query.strip():
        return {"data": "", "count": 0, "dataset_ids": []}

    results = []
    
    # --- Step 1: Retrieval ---
    if request.search_type == "keyword":
        results = await MetadataV2Service.keyword_search(request.data_source, request.query)
    else:
        # 调用 VectorService 核心语义搜索逻辑
        from app.services.vector_service import VectorService
        results = await VectorService.semantic_search(
            request.data_source, 
            request.query, 
            enable_rerank=request.enable_rerank
        )

    if not results:
        return {"data": "", "count": 0, "dataset_ids": []}

    # --- Step 2: Granular Context Assembly (Synchronized with V2 logic) ---
    yaml_list = []
    dataset_ids = set()
    seen_items = set() # Set of (type, id)
    
    for res in results:
        item_type = res.get('item_type')
        item_id = res.get('item_id')
        ds_id = res.get('dataset_id')
        
        if not item_type or not item_id:
            continue
            
        dataset_ids.add(ds_id)
        
        # Deduplication
        item_key = (item_type, item_id)
        if item_key in seen_items:
            continue
        seen_items.add(item_key)
        
        # Handle Keyword Result (Fetch from DB)
        if request.search_type == "keyword":
            if item_type == "table":
                table = await MetadataV2Service.get_table_by_id(item_id)
                if table: yaml_list.append(MetadataYamlService.generate_table_yaml(table))
            elif item_type == "metric":
                metric = await MetadataV2Service.get_metric_by_id(item_id)
                if metric: yaml_list.append(MetadataYamlService.generate_metric_yaml(metric))
        
        # Handle Semantic Result (Prefer Redis Content if available)
        else:
            yaml_content = res.get('yaml_content')
            if yaml_content:
                yaml_list.append(yaml_content)
            else:
                # Fallback to DB
                if item_type == "table":
                    table = await MetadataV2Service.get_table_by_id(item_id)
                    if table: yaml_list.append(MetadataYamlService.generate_table_yaml(table))
                elif item_type == "metric":
                    metric = await MetadataV2Service.get_metric_by_id(item_id)
                    if metric: yaml_list.append(MetadataYamlService.generate_metric_yaml(metric))
    
    combined_yaml = MetadataYamlService.combine_yamls(yaml_list)
    
    return {
        "data": combined_yaml,
        "count": len(dataset_ids),
        "dataset_ids": list(dataset_ids)
    }
