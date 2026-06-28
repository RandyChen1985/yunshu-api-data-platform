from fastapi import APIRouter, Depends, Query, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List
from app.core.dependencies import require_api_key, require_admin
from app.core.database import get_db_connection
from app.utils.sharding import get_audit_table_name, get_sharding_queries
from datetime import datetime, timedelta
import json
import csv
import io

router = APIRouter()

class LogExportRequest(BaseModel):
    sql: str
    row_count: int
    data_source: str
    format: str

def is_admin(user: dict) -> bool:
    """Check if user has admin role"""
    if user.get("role") == "admin":
        return True
    perms = user.get("permissions")
    if not perms:
        return False
    if isinstance(perms, str):
         try:
             perms = json.loads(perms)
         except:
             return False
    return perms.get("role") == "admin"

def build_union_all_query(tables: List[str], where_clause: str, select_fields: str = "*", limit: int = 0, order_by_clause: str = "") -> str:
    """
    Helper to build UNION ALL query for multiple sharded tables.
    Supports optimization by pushing down ORDER BY and LIMIT to sub-queries.
    """
    queries = []
    for table in tables:
        q = f"SELECT {select_fields} FROM {table} {where_clause}"
        if order_by_clause:
            q += f" {order_by_clause}"
        if limit > 0:
            q += f" LIMIT {limit}"
        queries.append(f"({q})") # Parentheses are required for UNION with LIMIT/ORDER
        
    return " UNION ALL ".join(queries)

@router.post("/logs/custom_export")
async def log_custom_export(
    request_in: Request,
    req: LogExportRequest,
    user: dict = Depends(require_api_key)
):
    """Manual trigger to log a data export event from frontend"""
    request_in.state.action_type = 'LAB_EXPORT'
    request_in.state.source_sql = req.sql
    return {"status": "success"}

@router.get("/logs/export")
async def export_logs(
    format: str = Query("csv", pattern="^(csv|json)$"),
    user_name: Optional[str] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    method: Optional[str] = None,
    status_code: Optional[int] = None,
    endpoint: Optional[str] = None,
    client_ip: Optional[str] = None,
    action_type: Optional[str] = Query(None),
    user: dict = Depends(require_api_key)
):
    """Export audit logs from daily sharded tables."""
    admin_flag = is_admin(user)
    target_user = user_name if admin_flag else user["user_name"]
    
    async with get_db_connection() as conn:
        try:
            tables = await get_sharding_queries(conn, start_time, end_time)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        if not tables:
            raise HTTPException(status_code=400, detail="No logs found for the selected range.")

        # Build WHERE
        query_conditions = []
        params = []
        if target_user:
            query_conditions.append("user_name = %s")
            params.append(target_user)
        
        now = datetime.now()
        # 清洗时间参数
        final_start = (start_time.replace('T', ' ') if start_time else now.strftime('%Y-%m-%d 00:00:00'))
        final_end = (end_time.replace('T', ' ') if end_time else now.strftime('%Y-%m-%d %H:%M:%S'))
        
        query_conditions.append("created_at >= %s")
        params.append(final_start)
        query_conditions.append("created_at <= %s")
        params.append(final_end)

        if method: query_conditions.append("method = %s"); params.append(method)
        if status_code: query_conditions.append("status_code = %s"); params.append(status_code)
        if endpoint: query_conditions.append("endpoint LIKE %s"); params.append(f"%{endpoint}%")
        if client_ip: query_conditions.append("client_ip LIKE %s"); params.append(f"%{client_ip}%")
        if action_type: query_conditions.append("action_type = %s"); params.append(action_type)

        where_clause = "WHERE " + " AND ".join(query_conditions) if query_conditions else ""
        all_params = tuple(params * len(tables))

        async with conn.cursor() as cursor:
            # Check count
            union_count = build_union_all_query(tables, where_clause, "id")
            await cursor.execute(f"SELECT COUNT(*) FROM ({union_count}) AS total", all_params)
            total = (await cursor.fetchone())[0]
            
            if total > 10000:
                raise HTTPException(status_code=400, detail=f"Too many records ({total}). Max 10000.")

            # Define standard columns
            columns = ["id", "trace_id", "user_name", "endpoint", "method", "status_code", "process_time_ms", "client_ip", "action_type", "created_at"]
            rows = []

            if total > 0:
                # Fetch
                fields = ", ".join(columns)
                union_data = build_union_all_query(tables, where_clause, fields)
                sql = f"SELECT * FROM ({union_data}) AS data ORDER BY created_at DESC LIMIT 10000"
                await cursor.execute(sql, all_params)
                rows = await cursor.fetchall()
            
            if format == "csv":
                output = io.StringIO()
                writer = csv.DictWriter(output, fieldnames=columns)
                writer.writeheader()
                for row in rows: writer.writerow(dict(zip(columns, row)))
                content = output.getvalue(); output.close()
                filename = f"audit_{now.strftime('%Y%m%d')}.csv"
                return StreamingResponse(iter([content]), media_type="text/csv", 
                    headers={"Content-Disposition": f"attachment; filename={filename}"})
            else:
                items = [dict(zip(columns, row)) for row in rows]
                result = {"total": len(items), "items": items}
                return StreamingResponse(iter([json.dumps(result, default=str, ensure_ascii=False)]), media_type="application/json",
                    headers={"Content-Disposition": f"attachment; filename=audit_{now.strftime('%Y%m%d')}.json"})

@router.get("/logs")
async def get_audit_logs(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    user_name: Optional[str] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    method: Optional[str] = None,
    status_code: Optional[int] = None,
    min_status: Optional[int] = None,
    max_status: Optional[int] = None,
    endpoint: Optional[str] = None,
    client_ip: Optional[str] = None,
    action_type: Optional[str] = Query(None),
    include_stats: bool = False,
    user: dict = Depends(require_api_key)
):
    """Get audit logs from daily sharded tables (Max 3 days span)"""
    admin_flag = is_admin(user)
    target_user = user["user_name"] if not admin_flag else user_name

    async with get_db_connection() as conn:
        try:
            tables = await get_sharding_queries(conn, start_time, end_time)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        if not tables:
            return {
                "total": 0, "page": page, "size": size, "items": [], 
                "statistics": {
                    "total_requests": 0, "success_count": 0, "error_count": 0,
                    "success_rate": 0, "avg_response_time": 0
                } if include_stats else None
            }

        query_conditions = []
        params = []
        if target_user:
            query_conditions.append("user_name = %s")
            params.append(target_user)
        
        now = datetime.now()
        # 强制格式化时间，确保秒数存在且去掉 T 字符
        if start_time:
            final_start = start_time.replace('T', ' ')
            if len(final_start) == 16: final_start += ":00"
        else:
            final_start = now.strftime('%Y-%m-%d 00:00:00')

        if end_time:
            final_end = end_time.replace('T', ' ')
            if len(final_end) == 16: final_end += ":59"
        else:
            final_end = now.strftime('%Y-%m-%d %H:%M:%S')
        
        query_conditions.append("created_at >= %s")
        params.append(final_start)
        query_conditions.append("created_at <= %s")
        params.append(final_end)
        
        if method: query_conditions.append("method = %s"); params.append(method)
        if status_code: query_conditions.append("status_code = %s"); params.append(status_code)
        if min_status: query_conditions.append("status_code >= %s"); params.append(min_status)
        if max_status: query_conditions.append("status_code <= %s"); params.append(max_status)
        if endpoint: query_conditions.append("endpoint LIKE %s"); params.append(f"%{endpoint}%")
        if client_ip: query_conditions.append("client_ip LIKE %s"); params.append(f"%{client_ip}%")
        if action_type: query_conditions.append("action_type = %s"); params.append(action_type)
            
        where_clause = "WHERE " + " AND ".join(query_conditions) if query_conditions else ""
        offset = (page - 1) * size
        all_params = tuple(params * len(tables))

        async with conn.cursor() as cursor:
            # 回归精确计数，排除估算干扰
            union_all_sql = build_union_all_query(tables, where_clause, "id")
            count_sql = f"SELECT COUNT(*) FROM ({union_all_sql}) AS total"
            await cursor.execute(count_sql, all_params)
            total = (await cursor.fetchone())[0]

            statistics = None
            if include_stats:
                # --- 优化点：利用预聚合表加速统计 ---
                # 如果查询条件简单（聚合表包含 user_name, action_type, endpoint[部分匹配较难], method[暂无]），
                # 我们可以尝试从 api_access_stats_1m 读统计数据。
                # 注意：目前统计表仅按 user_name 聚合，且 endpoint = 'ALL' 代表该用户全量。
                
                is_stats_optimizable = not any([status_code, min_status, max_status, client_ip, method])
                # 如果有具体的 endpoint 搜索，聚合表目前可能由于是 ALL 记录而无法准确匹配，暂不优化。
                if endpoint: is_stats_optimizable = False 

                if is_stats_optimizable:
                    try:
                        # 构建聚合表查询
                        stats_cond = ["time_bucket >= %s", "time_bucket <= %s"]
                        stats_params = [final_start, final_end]
                        
                        if target_user:
                            stats_cond.append("user_name = %s")
                            stats_params.append(target_user)
                        else:
                            stats_cond.append("user_name = 'ALL'")
                        
                        # 功能点过滤
                        if action_type:
                            stats_cond.append("endpoint = %s") # 统计表中 endpoint 字段有时用于存 action_type，需确认逻辑
                            # 实际上当前的 api_access_stats_1m 可能不完全支持 action_type 过滤，
                            # 如果有 action_type 过滤，我们保守起见回归原始表。
                            is_stats_optimizable = False 
                        
                        if is_stats_optimizable:
                            stats_sql = f"""
                                SELECT 
                                    SUM(total_calls) as total_requests,
                                    SUM(total_calls - total_error) as success_count,
                                    SUM(total_error) as error_count,
                                    SUM(total_calls * avg_latency) / NULLIF(SUM(total_calls), 0) as avg_response_time
                                FROM api_access_stats_1m
                                WHERE {" AND ".join(stats_cond)}
                            """
                            await cursor.execute(stats_sql, tuple(stats_params))
                            row = await cursor.fetchone()
                            if row and row[0]:
                                total_req = int(row[0])
                                success_ct = int(row[1] or 0)
                                statistics = {
                                    "total_requests": total_req,
                                    "success_count": success_ct,
                                    "error_count": int(row[2] or 0),
                                    "success_rate": round(success_ct / total_req * 100, 2) if total_req > 0 else 0,
                                    "avg_response_time": round(float(row[3] or 0), 2)
                                }
                    except Exception as e:
                        logger.warning(f"Failed to fetch stats from aggregation table: {e}")

                # 如果无法优化或优化查询失败，执行原始表聚合
                if statistics is None and total > 0:
                    stats_fields = """
                        COUNT(*) as total_requests,
                        SUM(CASE WHEN status_code >= 200 AND status_code < 300 THEN 1 ELSE 0 END) as success_count,
                        SUM(CASE WHEN status_code >= 400 THEN 1 ELSE 0 END) as error_count,
                        AVG(process_time_ms) as avg_response_time
                    """
                    stats_union = build_union_all_query(tables, where_clause, stats_fields)
                    stats_sql = f"SELECT SUM(total_requests), SUM(success_count), SUM(error_count), AVG(avg_response_time) FROM ({stats_union}) AS gs"
                    await cursor.execute(stats_sql, all_params)
                    row = await cursor.fetchone()
                    if row:
                        total_req = row[0] or 0
                        success_ct = row[1] or 0
                        statistics = {
                            "total_requests": int(total_req),
                            "success_count": int(success_ct),
                            "error_count": int(row[2] or 0),
                            "success_rate": round(success_ct / total_req * 100, 2) if total_req > 0 else 0,
                            "avg_response_time": round(float(row[3] or 0), 2)
                        }
                elif statistics is None:
                    statistics = {
                        "total_requests": 0, "success_count": 0, "error_count": 0,
                        "success_rate": 0, "avg_response_time": 0
                    }

            fields = "id, trace_id, user_name, endpoint, method, status_code, process_time_ms, client_ip, action_type, created_at"
            
            # Optimization: Push down LIMIT and ORDER BY to sub-queries
            # We must fetch (offset + size) rows from EACH table to ensure correct global ordering after UNION
            sub_limit = offset + size
            
            data_union = build_union_all_query(
                tables, 
                where_clause, 
                fields, 
                limit=sub_limit, 
                order_by_clause="ORDER BY created_at DESC"
            )
            
            data_sql = f"SELECT * FROM ({data_union}) AS data ORDER BY created_at DESC LIMIT %s OFFSET %s"
            await cursor.execute(data_sql, all_params + (size, offset))
            rows = await cursor.fetchall()
            columns = [col[0] for col in cursor.description]
            items = [dict(zip(columns, row)) for row in rows]

            return {"total": total, "page": page, "size": size, "items": items, "statistics": statistics}

@router.get("/logs/{log_id}")
async def get_log_detail(
    log_id: int,
    date: Optional[str] = Query(None, description="Date of the log (YYYY-MM-DD). Optional but faster."),
    user: dict = Depends(require_api_key)
):
    """Get log detail. Scans recent 3 days if date is not provided."""
    admin_flag = is_admin(user)
    if date:
        tables = [f"api_access_logs_{date.replace('-', '')}"]
    else:
        now = datetime.now()
        tables = [get_audit_table_name(now - timedelta(days=i)) for i in range(3)]

    async with get_db_connection() as conn:
        async with conn.cursor() as cursor:
            for table in tables:
                try:
                    await cursor.execute(f"SHOW TABLES LIKE '{table}'")
                    if not await cursor.fetchone(): continue
                    sql = f"SELECT * FROM {table} WHERE id = %s"
                    params = [log_id]
                    if not admin_flag:
                        sql += " AND user_name = %s"; params.append(user["user_name"])
                    await cursor.execute(sql, tuple(params))
                    row = await cursor.fetchone()
                    if row:
                        columns = [col[0] for col in cursor.description]
                        detail = dict(zip(columns, row))
                        for field in ["request_params", "response_body"]:
                            if detail.get(field):
                                try: detail[field] = json.loads(detail[field])
                                except: pass
                        return detail
                except Exception: continue
            raise HTTPException(status_code=404, detail="Log not found")
