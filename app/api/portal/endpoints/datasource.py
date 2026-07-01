from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional, Dict
import asyncio
from app.schemas.datasource import DataSourceCreate, DataSourceUpdate, DataSourceResponse
from app.services.datasource_service import DataSourceService
from app.core.dependencies import require_admin, require_api_key, require_permission
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/datasources", response_model=List[DataSourceResponse])
async def list_datasources(
    status: Optional[str] = None,
    user: dict = Depends(require_api_key)
):
    """
    List data sources with optional status filter.
    """
    datasources = await DataSourceService.list_datasources(status=status)
    return datasources

@router.post("/datasources", response_model=DataSourceResponse)
async def create_datasource(
    datasource: DataSourceCreate,
    user: dict = Depends(require_permission("element:datasource:edit"))
):
    """
    Create a new data source.
    Admin only.
    """
    try:
        # Check if exists
        existing = await DataSourceService.get_datasource_by_name(datasource.source_name)
        if existing:
            raise HTTPException(status_code=400, detail=f"Data source {datasource.source_name} already exists")
        
        new_datasource = await DataSourceService.create_datasource(datasource)
        return new_datasource
    except Exception as e:
        logger.error(f"Failed to create data source: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/datasources/{source_id}", response_model=DataSourceResponse)
async def get_datasource(
    source_id: int,
    user: dict = Depends(require_api_key)
):
    """
    Get data source by ID.
    Admin only.
    """
    datasource = await DataSourceService.get_datasource(source_id)
    if not datasource:
        raise HTTPException(status_code=404, detail="Data source not found")
    return datasource

@router.put("/datasources/{source_id}", response_model=DataSourceResponse)
async def update_datasource(
    source_id: int,
    update_data: DataSourceUpdate,
    user: dict = Depends(require_permission("element:datasource:edit"))
):
    """
    Update a data source.
    Admin only.
    """
    try:
        existing = await DataSourceService.get_datasource(source_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Data source not found")
        
        updated = await DataSourceService.update_datasource(source_id, update_data)
        return updated
    except Exception as e:
        logger.error(f"Failed to update data source: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/datasources/{source_id}", response_model=dict)
async def delete_datasource(
    source_id: int,
    user: dict = Depends(require_permission("element:datasource:edit"))
):
    """
    Delete a data source.
    Admin only.
    """
    try:
        success = await DataSourceService.delete_datasource(source_id)
        if not success:
            raise HTTPException(status_code=404, detail="Data source not found")
        return {"deleted_id": source_id, "message": "Data source deleted"}
    except ValueError as e:
        # Handle business logic errors (e.g., dependency check)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to delete data source: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/reorder", response_model=dict)
async def reorder_datasources(
    request: Dict[str, List[int]],
    user: dict = Depends(require_permission("element:datasource:edit"))
):
    """
    Update the sorting order of data sources.
    Expects JSON: {"ids": [3, 1, 2]}
    """
    try:
        ids = request.get("ids")
        if not ids:
            raise HTTPException(status_code=400, detail="Missing 'ids' list in request body")
        
        await DataSourceService.reorder_datasources(ids)
        return {"message": "Data sources reordered successfully"}
    except Exception as e:
        logger.error(f"Failed to reorder data sources: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/datasources/{source_id}/test", response_model=dict)
async def test_datasource_connection(
    source_id: int,
    user: dict = Depends(require_permission("element:datasource:edit"))
):
    """
    Test data source connection.
    Admin only.
    """
    try:
        from app.services.pool_manager import DataSourcePoolManager
        
        datasource = await DataSourceService.get_datasource(source_id)
        if not datasource:
            raise HTTPException(status_code=404, detail="Data source not found")
        
        # Try to get/create pool
        pool = await DataSourcePoolManager.get_pool(source_id)
        
        # Test connection
        if datasource.source_type == "clickhouse":
            async with pool.connection() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute("SELECT 1")
                    await cursor.fetchone()
        elif datasource.source_type == "mysql":
            async with pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute("SELECT 1")
                    await cursor.fetchone()
        elif datasource.source_type == "oracle":
            # Check if pool is sync (Thick Mode) or async (Thin Mode)
            is_async_pool = hasattr(pool, 'acquire') and asyncio.iscoroutinefunction(pool.acquire)
            
            if is_async_pool:
                conn = await pool.acquire()
                async with conn:
                    async with conn.cursor() as cursor:
                        await cursor.execute("SELECT 1 FROM DUAL")
                        await cursor.fetchone()
            else:
                # Synchronous acquire for Thick Mode
                def sync_test():
                    with pool.acquire() as conn:
                        with conn.cursor() as cursor:
                            cursor.execute("SELECT 1 FROM DUAL")
                            cursor.fetchone()
                await asyncio.to_thread(sync_test)
        elif datasource.source_type == "sqlserver":
            async with pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute("SELECT 1")
                    await cursor.fetchone()
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported source type: {datasource.source_type}")
        
        return {"status": "success", "message": "Connection successful"}
    except Exception as e:
        logger.error(f"Connection test failed: {e}")
        return {"status": "failed", "message": str(e)}
