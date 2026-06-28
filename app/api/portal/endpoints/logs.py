from fastapi import APIRouter, Depends, Query
from app.core.database import get_db_connection
from app.core.dependencies import require_api_key
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from app.utils.sharding import get_audit_table_name

router = APIRouter()

class AccessLogBase(BaseModel):
    id: int
    trace_id: str
    user_name: str
    method: str
    endpoint: str
    status_code: int
    process_time_ms: float
    client_ip: str
    created_at: datetime
    request_params: Optional[str] = None

@router.get("/access", response_model=List[AccessLogBase])
async def get_access_logs(
    resource_key: Optional[str] = None,
    limit: int = 50,
    current_user: dict = Depends(require_api_key)
):
    """
    Get recent access logs from DAILY SHARDED tables.
    """
    is_admin = current_user.get("role") == "admin"
    username = current_user.get("user_name")
    table_name = get_audit_table_name()

    async with get_db_connection() as conn:
        async with conn.cursor() as cursor:
            where_clauses = []
            params = []

            # 1. Filter by resource_key if provided
            if resource_key:
                if resource_key == 'system.sql.execute':
                    where_clauses.append("endpoint LIKE %s")
                    params.append('%/sql/execute')
                else:
                    where_clauses.append("endpoint LIKE %s")
                    params.append(f"%/{resource_key}%")
            
            # 2. Access Control: Regular users only see their own logs
            if not is_admin:
                where_clauses.append("user_name = %s")
                params.append(username)

            # Build SQL
            where_sql = ""
            if where_clauses:
                where_sql = "WHERE " + " AND ".join(where_clauses)
            
            try:
                sql = f"""
                    SELECT id, trace_id, user_name, method, endpoint, status_code, 
                           process_time_ms, client_ip, created_at, request_params
                    FROM {table_name}
                    {where_sql}
                    ORDER BY id DESC
                    LIMIT %s
                """
                params.append(limit)
                await cursor.execute(sql, tuple(params))
                rows = await cursor.fetchall()
            except Exception:
                # Table might not exist yet
                return []
            
            logs = []
            for row in rows:
                logs.append(AccessLogBase(
                    id=row[0],
                    trace_id=row[1],
                    user_name=row[2],
                    method=row[3],
                    endpoint=row[4],
                    status_code=row[5],
                    process_time_ms=row[6],
                    client_ip=row[7],
                    created_at=row[8],
                    request_params=row[9]
                ))
            return logs
