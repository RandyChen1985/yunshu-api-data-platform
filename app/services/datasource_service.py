import json
from typing import Optional, List, Dict
from datetime import datetime
from app.core.database import get_db_connection
from app.schemas.datasource import DataSourceCreate, DataSourceUpdate, DataSourceResponse, DataSourceInternal
import logging

logger = logging.getLogger(__name__)

class DataSourceService:
    """Service for managing data sources"""
    
    @classmethod
    async def list_datasources(cls, status: Optional[str] = None) -> List[DataSourceInternal]:
        """List data sources with optional status filter"""
        async with get_db_connection() as conn:
            async with conn.cursor() as cursor:
                sql = """
                    SELECT id, source_name, source_type, host, port, database_name,
                           username, password, extra_params, description, sort_order, status,
                           created_at, updated_at
                    FROM sys_data_source
                """
                params = []
                if status:
                    # Map semantic status to database integer values
                    db_status = 1 if status == 'active' else 0
                    sql += " WHERE status = %s"
                    params.append(db_status)
                
                sql += " ORDER BY sort_order ASC, id DESC"
                
                await cursor.execute(sql, tuple(params))
                rows = await cursor.fetchall()
                return [cls._map_row_to_model(row) for row in rows]
    
    @classmethod
    async def get_datasource(cls, source_id: int) -> Optional[DataSourceInternal]:
        """Get data source by ID"""
        async with get_db_connection() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    """
                    SELECT id, source_name, source_type, host, port, database_name,
                           username, password, extra_params, description, sort_order, status,
                           created_at, updated_at
                    FROM sys_data_source
                    WHERE id = %s
                    """,
                    (source_id,)
                )
                row = await cursor.fetchone()
                if not row:
                    return None
                return cls._map_row_to_model(row)
    
    @classmethod
    async def get_datasource_by_name(cls, source_name: str) -> Optional[DataSourceInternal]:
        """Get data source by name"""
        async with get_db_connection() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    """
                    SELECT id, source_name, source_type, host, port, database_name,
                           username, password, extra_params, description, sort_order, status,
                           created_at, updated_at
                    FROM sys_data_source
                    WHERE source_name = %s
                    """,
                    (source_name,)
                )
                row = await cursor.fetchone()
                if not row:
                    return None
                return cls._map_row_to_model(row)
    
    @classmethod
    async def create_datasource(cls, datasource: DataSourceCreate) -> DataSourceInternal:
        """Create a new data source"""
        extra_params_json = json.dumps(datasource.extra_params) if datasource.extra_params else None
        
        async with get_db_connection() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    """
                    INSERT INTO sys_data_source 
                    (source_name, source_type, host, port, database_name, username, 
                     password, extra_params, description, sort_order, status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        datasource.source_name, datasource.source_type, datasource.host,
                        datasource.port, datasource.database_name, datasource.username,
                        datasource.password, extra_params_json, datasource.description,
                        datasource.sort_order, datasource.status
                    )
                )
                await conn.commit()
                source_id = cursor.lastrowid
                return await cls.get_datasource(source_id)

    @classmethod
    async def reorder_datasources(cls, ids: List[int]) -> bool:
        """Update the sort_order of datasources based on the provided list of IDs"""
        async with get_db_connection() as conn:
            async with conn.cursor() as cursor:
                for index, source_id in enumerate(ids):
                    await cursor.execute(
                        "UPDATE sys_data_source SET sort_order = %s WHERE id = %s",
                        (index, source_id)
                    )
                await conn.commit()
                return True
    
    @classmethod
    async def update_datasource(cls, source_id: int, update_data: DataSourceUpdate) -> Optional[DataSourceInternal]:
        """Update data source"""
        update_dict = update_data.model_dump(exclude_unset=True)
        if not update_dict:
            return await cls.get_datasource(source_id)
        
        set_clauses = []
        values = []
        
        for key, value in update_dict.items():
            if key == 'extra_params':
                value = json.dumps(value) if value else None
            set_clauses.append(f"{key} = %s")
            values.append(value)
        
        values.append(source_id)
        
        sql = f"UPDATE sys_data_source SET {', '.join(set_clauses)} WHERE id = %s"
        
        async with get_db_connection() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(sql, tuple(values))
                await conn.commit()
        
        # Invalidate pool cache for this datasource
        from app.services.pool_manager import DataSourcePoolManager
        await DataSourcePoolManager.invalidate_pool(source_id)
        
        return await cls.get_datasource(source_id)
    
    @classmethod
    async def delete_datasource(cls, source_id: int) -> bool:
        """Delete data source"""
        # First, check if input source_id is valid and get its name
        datasource = await cls.get_datasource(source_id)
        if not datasource:
            return False

        async with get_db_connection() as conn:
            async with conn.cursor() as cursor:
                # Check for usage in sys_resource_meta
                await cursor.execute(
                    "SELECT COUNT(*) FROM sys_resource_meta WHERE data_source = %s",
                    (datasource.source_name,)
                )
                (count,) = await cursor.fetchone()
                
                if count > 0:
                    raise ValueError(f"Cannot delete data source: {count} resources are using it.")

                await cursor.execute("DELETE FROM sys_data_source WHERE id = %s", (source_id,))
                await conn.commit()
                
                if cursor.rowcount > 0:
                    # Invalidate pool cache
                    from app.services.pool_manager import DataSourcePoolManager
                    await DataSourcePoolManager.invalidate_pool(source_id)
                    return True
                return False
    
    @staticmethod
    def _map_row_to_model(row: tuple) -> DataSourceInternal:
        """Map database row to Pydantic model"""
        (
            id, source_name, source_type, host, port, database_name,
            username, password, extra_params, description, sort_order, status,
            created_at, updated_at
        ) = row
        
        if extra_params and isinstance(extra_params, str):
            extra_params = json.loads(extra_params)
        
        return DataSourceInternal(
            id=id,
            source_name=source_name,
            source_type=source_type,
            host=host,
            port=port,
            database_name=database_name,
            username=username,
            password=password,
            extra_params=extra_params,
            description=description,
            sort_order=sort_order,
            status=status,
            created_at=created_at,
            updated_at=updated_at
        )