import logging
import datetime
import asyncio
import re
from app.core.database import get_db_connection

logger = logging.getLogger(__name__)

async def clean_old_access_logs(retention_days: int = None, operator: str = "SYSTEM"):
    """
    清理过期分表 (Daily Sharding) 并记录维护日志
    """
    start_time = datetime.datetime.now()
    task_id = 0
    total_dropped = 0
    tables_dropped = []
    
    try:
        async with get_db_connection() as conn:
            async with conn.cursor() as cursor:
                # 1. 插入初始任务记录 (确保这一步最先执行)
                await cursor.execute(
                    "INSERT INTO sys_maintenance_log (task_name, status, start_time, operator) VALUES (%s, %s, %s, %s)",
                    ("log_purge_sharded", "RUNNING", start_time, operator)
                )
                task_id = cursor.lastrowid
                await conn.commit()

                # 2. 获取保留天数
                if retention_days is None:
                    await cursor.execute("SELECT config_value FROM sys_config WHERE config_key = 'log.retention.raw_days'")
                    row = await cursor.fetchone()
                    retention_days = int(row[0]) if row else 7

                logger.info(f"Starting sharded log cleaning (Retention: {retention_days} days)...")
                
                # 3. 计算截止日期
                cutoff_dt = datetime.datetime.now() - datetime.timedelta(days=retention_days)
                cutoff_date_str = cutoff_dt.strftime('%Y%m%d')
                
                # 4. 扫描所有日志分表
                await cursor.execute("SHOW TABLES LIKE 'api_access_logs_20%%'")
                tables = [row[0] for row in await cursor.fetchall()]
                
                for table in tables:
                    # 提取日期后缀 (e.g. api_access_logs_20260130 -> 20260130)
                    match = re.search(r'api_access_logs_(\d{8})$', table)
                    if match:
                        table_date = match.group(1)
                        if table_date < cutoff_date_str:
                            logger.info(f"Dropping expired audit table: {table}")
                            await cursor.execute(f"DROP TABLE {table}")
                            total_dropped += 1
                            tables_dropped.append(table)
                
                # 5. 更新任务状态及详细摘要
                end_time = datetime.datetime.now()
                summary = f"Cutoff: {cutoff_date_str}. Found {len(tables)} shards, dropped {total_dropped}."
                if tables_dropped:
                    summary += f" Deleted: {', '.join(tables_dropped[:3])}{'...' if len(tables_dropped) > 3 else ''}"
                
                await cursor.execute(
                    "UPDATE sys_maintenance_log SET status = 'SUCCESS', end_time = %s, affected_rows = %s, error_message = %s WHERE id = %s",
                    (end_time, total_dropped, summary, task_id)
                )
                await conn.commit()
                logger.info(f"Sharded log cleaning finished. {summary}")
                
    except Exception as e:
        logger.error(f"Error in clean_old_access_logs (sharded): {e}")
        if task_id > 0:
            try:
                async with get_db_connection() as conn:
                    async with conn.cursor() as cursor:
                        await cursor.execute(
                            "UPDATE sys_maintenance_log SET status = 'FAILED', error_message = %s WHERE id = %s",
                            (f"Error: {str(e)}", task_id)
                        )
                        await conn.commit()
            except Exception as inner_e:
                logger.error(f"Failed to record failure status: {inner_e}")

