import logging
from datetime import datetime, timedelta
from typing import List, Set
import asyncio

# 全局缓存，记录已确认存在的表名，减少数据库 SHOW TABLES 压力
_EXISTING_TABLES: Set[str] = set()
_CACHE_LOCK: asyncio.Lock = None

def get_cache_lock():
    global _CACHE_LOCK
    if _CACHE_LOCK is None:
        _CACHE_LOCK = asyncio.Lock()
    return _CACHE_LOCK

def get_audit_table_name(dt: datetime = None) -> str:
    """根据日期获取表名"""
    if dt is None:
        dt = datetime.now()
    return f"api_access_logs_{dt.strftime('%Y%m%d')}"

async def ensure_audit_table_exists(conn) -> str:
    """
    确保当天的审计日志表存在。
    使用缓存、重试机制和存在性检查，确保高并发下的稳定性。
    """
    table_name = get_audit_table_name()
    
    # 1. 检查缓存 (快速路径)
    if table_name in _EXISTING_TABLES:
        return table_name
        
    # 2. 检查数据库并创建 (慢速路径)
    # 使用简单的重试逻辑，应对并发下的数据库锁等待或竞争
    max_retries = 3
    last_error = None
    lock = get_cache_lock()
    
    for attempt in range(max_retries):
        try:
            # 双重检查锁（针对单进程内的并发协程）
            async with lock:
                if table_name in _EXISTING_TABLES:
                    return table_name

            async with conn.cursor() as cursor:
                # 尝试建表
                # IF NOT EXISTS 能够处理大部分并发情况
                sql = f"CREATE TABLE IF NOT EXISTS {table_name} LIKE api_access_logs_template"
                await cursor.execute(sql)
                
                # 成功后更新缓存
                async with lock:
                    _EXISTING_TABLES.add(table_name)
                
                if attempt > 0:
                    logging.info(f"Ensured audit table exists: {table_name} (succeeded on attempt {attempt + 1})")
                else:
                    logging.info(f"Ensured audit table exists: {table_name}")
                
                return table_name

        except Exception as e:
            last_error = e
            logging.warning(f"Attempt {attempt + 1}/{max_retries} to ensure audit table {table_name} failed: {e}")
            
            # 关键修复：失败后，主动检查表是否其实已经由其他进程创建成功？
            try:
                if await _check_table_exists_in_db(conn, table_name):
                    logging.info(f"Table {table_name} found despite error, recovering.")
                    async with lock:
                        _EXISTING_TABLES.add(table_name)
                    return table_name
            except Exception as check_error:
                logging.warning(f"Failed to verify table existence during recovery: {check_error}")

            # 如果不是最后一次尝试，等待随机时间后重试
            if attempt < max_retries - 1:
                await asyncio.sleep(0.1 * (attempt + 1))
    
    # 重试耗尽，抛出异常。
    # 绝对不能返回旧表名 "api_access_logs"，因为它已被删除，会导致后续写入必然失败。
    logging.error(f"Critical: Failed to ensure audit table {table_name} after {max_retries} retries. Error: {last_error}")
    raise last_error

async def _check_table_exists_in_db(conn, table_name: str) -> bool:
    """辅助函数：直接查库确认表是否存在"""
    async with conn.cursor() as cursor:
        await cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
        return await cursor.fetchone() is not None

async def get_sharding_queries(conn, start_date: str = None, end_date: str = None) -> List[str]:
    """
    根据日期范围获取实际存在的表名列表。
    限制跨度不超过 3 天。
    """
    now = datetime.now()
    if not start_date:
        start_date = now.strftime('%Y-%m-%d 00:00:00')
    if not end_date:
        end_date = now.strftime('%Y-%m-%d %H:%M:%S')

    try:
        # 增强解析逻辑，兼容斜杠和横杠
        s_str = start_date[:10].replace('/', '-')
        e_str = end_date[:10].replace('/', '-')
        s_dt = datetime.strptime(s_str, '%Y-%m-%d')
        e_dt = datetime.strptime(e_str, '%Y-%m-%d')
        # 将结束时间推到当天的最后一秒，确保涵盖当天分表
        e_dt = e_dt.replace(hour=23, minute=59, second=59)
    except Exception as e:
        logging.warning(f"Date parse failed for {start_date} - {end_date}: {e}")
        s_dt = now.replace(hour=0, minute=0, second=0, microsecond=0)
        e_dt = now.replace(hour=23, minute=59, second=59, microsecond=0)

    # 限制 3 天
    if (e_dt - s_dt).days > 3:
        raise ValueError("查询时间跨度不能超过 3 天")

    candidate_tables = []
    curr = s_dt
    while curr <= e_dt:
        candidate_tables.append(get_audit_table_name(curr))
        curr += timedelta(days=1)
    
    # 过滤掉不存在的表
    existing_tables = []
    async with conn.cursor() as cursor:
        for table in candidate_tables:
            # 使用简单的 SHOW TABLES 检查
            await cursor.execute(f"SHOW TABLES LIKE '{table}'")
            if await cursor.fetchone():
                existing_tables.append(table)
        
    return existing_tables
