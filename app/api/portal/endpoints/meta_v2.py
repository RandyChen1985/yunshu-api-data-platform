from fastapi import APIRouter, HTTPException, Depends, Body, BackgroundTasks, Request
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from app.services.metadata_v2_service import MetadataV2Service
from app.services.metadata_generator import MetadataGeneratorService
from app.services.metadata_yaml_service import MetadataYamlService
from app.services.vector_service import VectorService
from app.core.dependencies import require_admin, require_permission, require_api_key

router = APIRouter()

# --- Request Schemas ---

class ImportRequest(BaseModel):
    content: str = Field(..., description="内容")

class DatasetCreate(BaseModel):
    name: str = Field(..., description="数据集名称")
    display_name: Optional[str] = Field(None, description="展示名称")
    description: Optional[str] = Field(None, description="描述")
    data_source: Optional[str] = Field("default", description="数据源")
    tags: Optional[List[str]] = Field([], description="标签")

class SimulatorSearchRequest(BaseModel):
    query: str = Field(..., description="查询语句")
    data_source: str = Field(..., description="数据源")
    search_type: str = Field("keyword", description="搜索类型: keyword | semantic")
    enable_rerank: bool = Field(False, description="是否启用重排序")

class SearchResponse(BaseModel):
    data: str = Field(..., description="YAML 内容")
    count: int = Field(..., description="涉及数据集数量")
    dataset_ids: List[int] = Field(..., description="数据集 ID 列表")
    debug_logs: List[str] = Field(..., description="调试日志")

# --- API Endpoints ---

@router.post("/search", response_model=SearchResponse)
async def search_metadata(request_in: Request, request: SimulatorSearchRequest, user=Depends(require_api_key)):
    """
    元数据通用检索接口：支持全域 RAG 召回。
    """
    request_in.state.action_type = 'META_V2_SEARCH'
    debug_logs = []

    debug_logs.append(f"🏁 开始全域检索会话 (Session Start)")

    debug_logs.append(f"📝 用户提问: '{request.query}'")

    debug_logs.append(f"🌍 目标数据源: '{request.data_source}'")

    

    if not request.query.strip():

        return {"data": "", "count": 0, "dataset_ids": [], "debug_logs": debug_logs}



    results = []

    

    # --- Strategy 1: Keyword Search ---

    if request.search_type == "keyword":

        debug_logs.append(f"🕹️ 命中策略: 关键词模糊匹配 (Keyword Search)")

        debug_logs.append(f"⚙️ 执行逻辑: MySQL LIKE '%{request.query}%'")

        

        # 修复参数缺失问题，传入 data_source

        results = await MetadataV2Service.keyword_search(request.data_source, request.query)

        debug_logs.append(f"✅ 检索完成: 数据库命中 {len(results)} 条记录")

        

    # --- Strategy 2: Semantic Search ---

    else:

        debug_logs.append(f"🕹️ 命中策略: 语义向量检索 (Semantic Search)")
        if request.enable_rerank:
             debug_logs.append(f"🚀 [Rerank] 已启用精排 (Top-K Expansion -> Cross-Encoder)")

        debug_logs.append(f"🧠 [Step 1] 意图向量化: 调用 Embedding 模型生成 Query Vector...")

        

        # 语义搜索

        results = await VectorService.semantic_search(request.data_source, request.query, enable_rerank=request.enable_rerank)

        

        if results:

            debug_logs.append(f"🔍 [Step 2] Redis 向量召回{' + Rerank 精排' if request.enable_rerank else ''}: 成功命中 {len(results)} 个语义单元")

            for idx, res in enumerate(results):

                # Format: "命中table: tbl_user (Distance: 0.1234)"

                debug_logs.append(f"   ├─ [{idx+1}] Dataset {res['dataset_id']}: {res['reasons']}")

        else:

            debug_logs.append(f"⚠️ [Step 2] Redis 向量召回: 未找到符合阈值的相似向量 (Count=0)")



    if not results:
        debug_logs.append("❌ 最终结果: 未找到任何匹配的元数据资产")
        return {"data": "", "count": 0, "dataset_ids": [], "debug_logs": debug_logs}

    # --- Result Aggregation & Granular Context Assembly ---
    debug_logs.append(f"📦 [Step 3] 语义上下文原子化装配 (Granular Assembly)...")
    
    yaml_list = []
    dataset_ids = set()
    
    # Track items to avoid duplicates
    seen_items = set() # Set of (type, id)
    
    for res in results:
        item_type = res.get('item_type')
        item_id = res.get('item_id')
        ds_id = res.get('dataset_id')
        
        if not item_type or not item_id:
            continue
            
        dataset_ids.add(ds_id)
        
        # Check for duplicates
        item_key = (item_type, item_id)
        if item_key in seen_items:
            continue
        seen_items.add(item_key)
        
        # --- Handle Keyword Result (Fetch from DB) ---
        if request.search_type == "keyword":
            if item_type == "table":
                table = await MetadataV2Service.get_table_by_id(item_id)
                if table:
                    debug_logs.append(f"   ├─ 装配表: '{table['physical_name']}' (ID={item_id})")
                    yaml_list.append(MetadataYamlService.generate_table_yaml(table))
            elif item_type == "metric":
                metric = await MetadataV2Service.get_metric_by_id(item_id)
                if metric:
                    debug_logs.append(f"   ├─ 装配指标: '{metric['display_name']}' (ID={item_id})")
                    yaml_list.append(MetadataYamlService.generate_metric_yaml(metric))
        
        # --- Handle Semantic Result (Prefer Redis Content) ---
        else:
            # We already have the YAML fragment from Redis
            yaml_content = res.get('yaml_content')
            if yaml_content:
                debug_logs.append(f"   ├─ 提取片段: {res['reasons']}")
                yaml_list.append(yaml_content)
            else:
                # Fallback to DB if Redis content missing
                debug_logs.append(f"   ├─ 片段缺失，回源装配: {item_type} ID={item_id}")
                if item_type == "table":
                    table = await MetadataV2Service.get_table_by_id(item_id)
                    if table: yaml_list.append(MetadataYamlService.generate_table_yaml(table))
                elif item_type == "metric":
                    metric = await MetadataV2Service.get_metric_by_id(item_id)
                    if metric: yaml_list.append(MetadataYamlService.generate_metric_yaml(metric))
    
    combined_yaml = MetadataYamlService.combine_yamls(yaml_list)
    debug_logs.append(f"📄 会话结束: 已召回 {len(seen_items)} 个原子对象，生成 {len(combined_yaml)} 字符的上下文")
    
    return {
        "data": combined_yaml,
        "count": len(dataset_ids),
        "dataset_ids": list(dataset_ids),
        "debug_logs": debug_logs
    }

@router.get("/vector/browse")
async def browse_vectors(
    data_source: Optional[str] = None, 
    dataset_id: Optional[int] = None, 
    page: int = 1, 
    page_size: int = 20,
    user=Depends(require_permission("element:metadata:view"))
):
    """浏览 Redis 中的向量数据"""
    return await VectorService.list_vectors(data_source, dataset_id, page, page_size)

@router.get("/vector/details")
async def get_vector_details(
    key: str,
    user=Depends(require_permission("element:metadata:view"))
):
    """获取单个向量数据的详细信息"""
    return await VectorService.get_vector_details(key)

@router.get("/stats")
async def get_stats(data_source: Optional[str] = None, user=Depends(require_permission("element:metadata:view"))):
    """获取元数据统计信息"""
    return await MetadataV2Service.get_stats(data_source)

@router.get("/datasets")
async def list_datasets(user=Depends(require_permission("element:metadata:view"))):
    return await MetadataV2Service.get_datasets()

@router.get("/datasets/{dataset_id}")
async def get_dataset(dataset_id: int, user=Depends(require_permission("element:metadata:view"))):
    dataset = await MetadataV2Service.get_dataset_by_id(dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return dataset

@router.post("/datasets")
async def create_dataset(request_in: Request, data: DatasetCreate, user=Depends(require_permission("element:metadata:manage"))):
    request_in.state.action_type = 'META_V2_DATASET_CREATE'
    try:
        dataset_id = await MetadataV2Service.create_dataset(data.dict(), created_by=user.get("user_id"))
        return {"id": dataset_id, "status": "success"}
    except Exception as e:
        # 捕获 MySQL 唯一键冲突 (Error 1062)
        if "1062" in str(e) or "Duplicate entry" in str(e):
            raise HTTPException(status_code=400, detail=f"数据集编码 '{data.name}' 已存在，请更换")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/datasets/{dataset_id}")
async def update_dataset(request_in: Request, dataset_id: int, data: Dict[str, Any] = Body(...), user=Depends(require_permission("element:metadata:manage"))):
    request_in.state.action_type = 'META_V2_DATASET_UPDATE'
    # 更新操作通常不改变创建人
    await MetadataV2Service.update_dataset(dataset_id, data)
    return {"status": "success"}

@router.post("/datasets/analyze-ddl")
async def analyze_ddl(request_in: Request, request: ImportRequest, user=Depends(require_permission("element:metadata:manage"))):
    """智能解析 DDL 并返回结构化预览"""
    request_in.state.action_type = 'META_V2_DDL_ANALYZE'
    try:
        result = await MetadataGeneratorService.generate_from_content(request.content)
        return {"data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ai/suggest-description")
async def suggest_description(request_in: Request, data: Dict[str, Any] = Body(...), user=Depends(require_permission("element:metadata:manage"))):
    """利用 AI 润色或预测业务描述"""
    request_in.state.action_type = 'META_V2_DESC_SUGGEST'
    desc = await MetadataGeneratorService.suggest_description(data)
    return {"description": desc}

@router.post("/datasets/{dataset_id}/save-table")
async def save_table(request_in: Request, dataset_id: int, table_data: Dict[str, Any] = Body(...), user=Depends(require_permission("element:metadata:manage"))):
    """保存或更新单张表的元数据结果"""
    request_in.state.action_type = 'META_V2_TABLE_SAVE'
    table_id = await MetadataV2Service.save_table_metadata(dataset_id, table_data, created_by=user.get("user_id"))
    return {"id": table_id, "status": "success"}

@router.delete("/datasets/{dataset_id}/tables/{table_id}")
async def delete_table(request_in: Request, dataset_id: int, table_id: int, user=Depends(require_permission("element:metadata:manage"))):
    """从数据集中删除一张表的定义"""
    request_in.state.action_type = 'META_V2_TABLE_DELETE'
    await MetadataV2Service.delete_table(dataset_id, table_id)
    return {"status": "success"}

@router.post("/datasets/{dataset_id}/metrics")
async def create_metric(request_in: Request, dataset_id: int, data: Dict[str, Any] = Body(...), user=Depends(require_permission("element:metadata:manage"))):
    request_in.state.action_type = 'META_V2_METRIC_CREATE'
    await MetadataV2Service.create_metric(dataset_id, data, created_by=user.get("user_id"))
    return {"status": "success"}

@router.delete("/datasets/{dataset_id}/metrics/{metric_id}")
async def delete_metric(request_in: Request, dataset_id: int, metric_id: int, user=Depends(require_permission("element:metadata:manage"))):
    request_in.state.action_type = 'META_V2_METRIC_DELETE'
    await MetadataV2Service.delete_metric(dataset_id, metric_id)
    return {"status": "success"}

@router.post("/datasets/{dataset_id}/relationships")
async def create_relationship(request_in: Request, dataset_id: int, data: Dict[str, Any] = Body(...), user=Depends(require_permission("element:metadata:manage"))):
    request_in.state.action_type = 'META_V2_RELATION_CREATE'
    # Add dataset context to relationship if needed, though service currently only needs source/target table IDs
    await MetadataV2Service.create_relationship(dataset_id, data, created_by=user.get("user_id"))
    return {"status": "success"}

@router.delete("/datasets/{dataset_id}/relationships/{rel_id}")
async def delete_relationship(request_in: Request, dataset_id: int, rel_id: int, user=Depends(require_permission("element:metadata:manage"))):
    request_in.state.action_type = 'META_V2_RELATION_DELETE'
    await MetadataV2Service.delete_relationship(dataset_id, rel_id)
    return {"status": "success"}

@router.post("/datasets/{dataset_id}/metrics/recommend")
async def recommend_metrics(request_in: Request, dataset_id: int, user=Depends(require_permission("element:metadata:manage"))):
    """基于当前数据集的表结构，由 AI 推荐业务指标"""
    request_in.state.action_type = 'META_V2_METRIC_RECOMMEND'
    dataset = await MetadataV2Service.get_dataset_by_id(dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    # 构建简单的表结构上下文供 AI 参考
    from app.services.metadata_yaml_service import MetadataYamlService
    schema_context = MetadataYamlService.generate_dataset_yaml(dataset)
    
    try:
        recommendations = await MetadataGeneratorService.recommend_metrics(schema_context)
        return {"data": recommendations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/datasets/{dataset_id}/relationships/recommend")
async def recommend_relationships(request_in: Request, dataset_id: int, user=Depends(require_permission("element:metadata:manage"))):
    """基于当前数据集的表结构，由 AI 智能发现表关联关系"""
    request_in.state.action_type = 'META_V2_RELATION_RECOMMEND'
    dataset = await MetadataV2Service.get_dataset_by_id(dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    schema_context = MetadataYamlService.generate_dataset_yaml(dataset)
    
    try:
        recommendations = await MetadataGeneratorService.recommend_relationships(schema_context)
        return {"data": recommendations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/datasets/{dataset_id}/usage")
async def get_dataset_usage(dataset_id: int, user=Depends(require_permission("element:metadata:view"))):
    """获取该数据集下表关联的接口列表"""
    data = await MetadataV2Service.get_dataset_usage(dataset_id)
    return {"data": data}

@router.get("/datasets/{dataset_id}/yaml")
async def get_dataset_yaml(dataset_id: int, user=Depends(require_permission("element:metadata:view"))):
    dataset = await MetadataV2Service.get_dataset_by_id(dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    yaml_str = MetadataYamlService.generate_dataset_yaml(dataset)
    return {"data": yaml_str}

@router.delete("/datasets/{dataset_id}")
async def delete_dataset(request_in: Request, dataset_id: int, user=Depends(require_permission("element:metadata:manage"))):
    request_in.state.action_type = 'META_V2_DATASET_DELETE'
    # 1. 从 MySQL 中逻辑/物理删除
    await MetadataV2Service.delete_dataset(dataset_id)
    # 2. 从 Redis 向量库中同步删除关联向量
    await VectorService.purge_dataset(dataset_id)
    return {"status": "success"}

@router.post("/datasets/{dataset_id}/sync-vector")
async def sync_vector(request_in: Request, dataset_id: int, background_tasks: BackgroundTasks, user=Depends(require_permission("element:metadata:manage"))):
    """手动同步元数据到向量库 (Redis Stack)"""
    request_in.state.action_type = 'META_V2_VECTOR_SYNC'
    # 1. 检查数据集是否存在
    dataset = await MetadataV2Service.get_dataset_by_id(dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    # 2. 更新状态为 同步中 (2)
    await MetadataV2Service.update_dataset(dataset_id, {"vector_status": 2})
    
    # 3. 异步执行同步逻辑
    background_tasks.add_task(VectorService.sync_dataset, dataset_id)
    
    return {"status": "success", "message": "Synchronization started in background"}

@router.post("/datasets/{dataset_id}/ai-enrich")
async def ai_enrich_dataset(request_in: Request, dataset_id: int, user=Depends(require_permission("element:metadata:manage"))):
    """AI 一键批量修复/润色元数据"""
    request_in.state.action_type = 'META_V2_AI_ENRICH'
    await MetadataV2Service.batch_enrich_dataset(dataset_id)
    return {"status": "success", "message": "Metadata enrichment completed"}

@router.post("/datasets/{dataset_id}/health-check")
async def trigger_health_check(dataset_id: int, user=Depends(require_permission("element:metadata:view"))):
    """手动触发健康检查打分"""
    from app.services.meta_health_service import MetaHealthService
    result = await MetaHealthService.calculate_dataset_health(dataset_id)
    return result
