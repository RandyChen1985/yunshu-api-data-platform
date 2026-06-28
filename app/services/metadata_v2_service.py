import json
import logging
import asyncio
import aiomysql
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.core.database import get_db_connection

logger = logging.getLogger(__name__)

class MetadataV2Service:
    @staticmethod
    async def get_stats(data_source: Optional[str] = None) -> Dict[str, Any]:
        """获取元数据统计信息"""
        async with get_db_connection() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                if data_source:
                    await cursor.execute("SELECT COUNT(*) as dataset_count FROM meta_datasets WHERE data_source = %s", (data_source,))
                    dataset_count = (await cursor.fetchone())['dataset_count']
                    
                    await cursor.execute("SELECT COUNT(*) as table_count FROM meta_tables t JOIN meta_datasets d ON t.dataset_id = d.id WHERE d.data_source = %s", (data_source,))
                    table_count = (await cursor.fetchone())['table_count']
                else:
                    await cursor.execute("SELECT COUNT(*) as dataset_count FROM meta_datasets")
                    dataset_count = (await cursor.fetchone())['dataset_count']
                    
                    await cursor.execute("SELECT COUNT(*) as table_count FROM meta_tables")
                    table_count = (await cursor.fetchone())['table_count']
                
                return {
                    "dataset_count": dataset_count,
                    "table_count": table_count
                }

    @staticmethod
    async def _mark_as_stale(dataset_id: int):
        """将数据集标记为版本过时或待同步状态"""
        async with get_db_connection() as conn:
            async with conn.cursor() as cursor:
                # 逻辑：只有当状态为 1 (已同步) 时，才切换为 4 (待更新)
                # 如果本来就是 0 (未同步) 或 3 (失败)，则不改变其原始分类
                await cursor.execute(
                    "UPDATE meta_datasets SET vector_status = 4 WHERE id = %s AND vector_status = 1",
                    (dataset_id,)
                )
                # 如果当前没有状态（比如刚创建完表），也可以考虑补一个逻辑，但通常增删改都是针对已有数据的
                await conn.commit()

    # --- Dataset CRUD ---

    @staticmethod
    async def get_datasets() -> List[Dict[str, Any]]:
        async with get_db_connection() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                # 1. Fetch Datasets with creator info
                sql = """
                    SELECT d.*, u.user_name as creator_name,
                           (SELECT COUNT(*) FROM meta_tables WHERE dataset_id = d.id) as table_count,
                           (SELECT COUNT(*) FROM meta_metrics WHERE dataset_id = d.id) as metric_count
                    FROM meta_datasets d
                    LEFT JOIN api_users u ON d.created_by = u.id
                    ORDER BY d.id DESC
                """
                await cursor.execute(sql)
                datasets = await cursor.fetchall()
                
                if not datasets:
                    return []

                # 2. Fetch all tables (Optimization: Batch fetch)
                await cursor.execute("SELECT dataset_id, physical_name FROM meta_tables")
                all_tables = await cursor.fetchall()
                
                ds_tables = {} # dataset_id -> set(table_names)
                for t in all_tables:
                    ds_id = t['dataset_id']
                    if ds_id not in ds_tables:
                        ds_tables[ds_id] = set()
                    ds_tables[ds_id].add(t['physical_name'])

                # 3. Fetch all resources to calculate usage
                ds_sources = set(d['data_source'] for d in datasets)
                usage_map = {d['id']: 0 for d in datasets}

                if ds_sources:
                    placeholders = ', '.join(['%s'] * len(ds_sources))
                    await cursor.execute(f"""
                        SELECT data_source, resource_mode, table_name, custom_sql 
                        FROM sys_resource_meta 
                        WHERE data_source IN ({placeholders})
                    """, tuple(ds_sources))
                    resources = await cursor.fetchall()

                    # Calculate in memory to avoid N+1 queries
                    # Index datasets by source for faster lookup
                    ds_by_source = {}
                    for d in datasets:
                        src = d['data_source']
                        if src not in ds_by_source: ds_by_source[src] = []
                        ds_by_source[src].append(d['id'])

                    for res in resources:
                        r_source = res['data_source']
                        r_mode = res['resource_mode']
                        r_table = res.get('table_name')
                        r_sql = res.get('custom_sql') or ""

                        target_ds_ids = ds_by_source.get(r_source, [])
                        
                        for ds_id in target_ds_ids:
                            tables = ds_tables.get(ds_id, set())
                            if not tables: continue
                            
                            matched = False
                            if r_mode == 'TABLE' and r_table in tables:
                                matched = True
                            elif r_mode == 'SQL':
                                # Consistent with get_dataset_usage logic
                                for t in tables:
                                    if t in r_sql:
                                        matched = True
                                        break
                            
                            if matched:
                                usage_map[ds_id] += 1

                for ds in datasets:
                    ds['usage_count'] = usage_map.get(ds['id'], 0)
                    # 转换 datetime
                    if ds.get('last_vectorized_at'):
                        ds['last_vectorized_at'] = ds['last_vectorized_at'].strftime("%Y-%m-%d %H:%M:%S")
                    if isinstance(ds.get('tags'), str):
                        try:
                            ds['tags'] = json.loads(ds['tags'])
                        except:
                            ds['tags'] = []
                return datasets

    @staticmethod
    async def get_dataset_by_id(dataset_id: int) -> Optional[Dict[str, Any]]:
        async with get_db_connection() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                # 1. 获取基础信息 (关联创建人)
                sql = """
                    SELECT d.*, u.user_name as creator_name 
                    FROM meta_datasets d 
                    LEFT JOIN api_users u ON d.created_by = u.id 
                    WHERE d.id = %s
                """
                await cursor.execute(sql, (dataset_id,))
                dataset = await cursor.fetchone()
                if not dataset:
                    return None
                
                # 处理 Dataset 的标签
                if isinstance(dataset.get('tags'), str):
                    try:
                        dataset['tags'] = json.loads(dataset['tags'])
                    except:
                        dataset['tags'] = []
                
                # 处理健康检查报告
                if isinstance(dataset.get('health_report'), str):
                    try:
                        dataset['health_report'] = json.loads(dataset['health_report'])
                    except:
                        dataset['health_report'] = None
                
                # 2. 获取包含字段的表 (关联创建人)
                sql_tables = """
                    SELECT t.*, u.user_name as creator_name 
                    FROM meta_tables t 
                    LEFT JOIN api_users u ON t.created_by = u.id 
                    WHERE t.dataset_id = %s
                """
                await cursor.execute(sql_tables, (dataset_id,))
                tables = await cursor.fetchall()
                
                for table in tables:
                    # 处理 JSON 字段
                    if isinstance(table.get('synonyms'), str):
                        table['synonyms'] = json.loads(table['synonyms'])
                    
                    await cursor.execute("SELECT * FROM meta_columns WHERE table_id = %s", (table['id'],))
                    columns = await cursor.fetchall()
                    # 处理 Column 的 JSON 字段
                    for col in columns:
                        for field in ['enums', 'synonyms', 'examples']:
                            if isinstance(col.get(field), str):
                                col[field] = json.loads(col[field])
                    table['columns'] = columns
                
                dataset['tables'] = tables
                
                # 3. 获取指标 (关联创建人)
                sql_metrics = """
                    SELECT m.*, u.user_name as creator_name 
                    FROM meta_metrics m 
                    LEFT JOIN api_users u ON m.created_by = u.id 
                    WHERE m.dataset_id = %s
                """
                await cursor.execute(sql_metrics, (dataset_id,))
                dataset['metrics'] = await cursor.fetchall()
                
                # 4. 获取关系 (关联创建人)
                rel_sql = """
                    SELECT r.*, t1.physical_name as source_table, t2.physical_name as target_table,
                           u.user_name as creator_name
                    FROM meta_relationships r
                    JOIN meta_tables t1 ON r.source_table_id = t1.id
                    JOIN meta_tables t2 ON r.target_table_id = t2.id
                    LEFT JOIN api_users u ON r.created_by = u.id
                    WHERE t1.dataset_id = %s OR t2.dataset_id = %s
                """
                await cursor.execute(rel_sql, (dataset_id, dataset_id))
                dataset['relationships'] = await cursor.fetchall()
                
                return dataset

    @staticmethod
    async def create_dataset(data: Dict[str, Any], created_by: Optional[int] = None) -> int:
        tags_json = json.dumps(data.get('tags', []))
        async with get_db_connection() as conn:
            async with conn.cursor() as cursor:
                sql = """
                    INSERT INTO meta_datasets (name, display_name, description, tags, data_source, status, created_by)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                await cursor.execute(sql, (
                    data['name'], data.get('display_name'), data.get('description'),
                    tags_json, data.get('data_source', 'default'), data.get('status', 1),
                    created_by
                ))
                return cursor.lastrowid

    @staticmethod
    async def update_dataset(dataset_id: int, data: Dict[str, Any], mark_stale: bool = True):
        fields = []
        values = []
        for k, v in data.items():
            if k == 'tags' and isinstance(v, list):
                v = json.dumps(v)
            fields.append(f"{k} = %s")
            values.append(v)
        
        values.append(dataset_id)
        sql = f"UPDATE meta_datasets SET {', '.join(fields)} WHERE id = %s"
        
        async with get_db_connection() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(sql, tuple(values))
        
        if mark_stale:
            await MetadataV2Service._mark_as_stale(dataset_id)

    @staticmethod
    async def delete_dataset(dataset_id: int):
        async with get_db_connection() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("DELETE FROM meta_datasets WHERE id = %s", (dataset_id,))
                await conn.commit()

    @staticmethod
    async def delete_table(dataset_id: int, table_id: int):
        async with get_db_connection() as conn:
            async with conn.cursor() as cursor:
                # 物理删除表定义
                await cursor.execute("DELETE FROM meta_tables WHERE id = %s AND dataset_id = %s", (table_id, dataset_id))
                await conn.commit()
        # 标记为待同步
        await MetadataV2Service._mark_as_stale(dataset_id)

    # --- Table & Column Persistence ---

    @staticmethod
    async def save_table_metadata(dataset_id: int, table_data: Dict[str, Any], created_by: Optional[int] = None) -> int:
        """
        保存或更新表及其字段元数据 (Upsert 逻辑)
        """
        async with get_db_connection() as conn:
            async with conn.cursor() as cursor:
                # 1. 表级 Upsert
                await cursor.execute(
                    "SELECT id FROM meta_tables WHERE dataset_id = %s AND physical_name = %s",
                    (dataset_id, table_data['physical_name'])
                )
                row = await cursor.fetchone()
                
                synonyms_json = json.dumps(table_data.get('synonyms', []))
                
                if row:
                    table_id = row[0]
                    await cursor.execute(
                        "UPDATE meta_tables SET term = %s, description = %s, synonyms = %s WHERE id = %s",
                        (table_data['term'], table_data.get('description'), synonyms_json, table_id)
                    )
                else:
                    await cursor.execute(
                        "INSERT INTO meta_tables (dataset_id, physical_name, term, description, synonyms, created_by) VALUES (%s, %s, %s, %s, %s, %s)",
                        (dataset_id, table_data['physical_name'], table_data['term'], table_data.get('description'), synonyms_json, created_by)
                    )
                    table_id = cursor.lastrowid

                # 2. 字段级处理 (同步模式: 删除不再存在的字段，更新现有的)
                incoming_cols = table_data.get('columns', [])
                incoming_names = [c['physical_name'] for c in incoming_cols]
                
                if incoming_names:
                    # 删除旧字段
                    placeholders = ', '.join(['%s'] * len(incoming_names))
                    del_sql = f"DELETE FROM meta_columns WHERE table_id = %s AND physical_name NOT IN ({placeholders})"
                    await cursor.execute(del_sql, (table_id, *incoming_names))
                else:
                    await cursor.execute("DELETE FROM meta_columns WHERE table_id = %s", (table_id,))

                # 逐个保存字段
                for col in incoming_cols:
                    await cursor.execute(
                        "SELECT id FROM meta_columns WHERE table_id = %s AND physical_name = %s",
                        (table_id, col['physical_name'])
                    )
                    col_row = await cursor.fetchone()
                    
                    enums_j = json.dumps(col.get('enums', []))
                    synonyms_j = json.dumps(col.get('synonyms', []))
                    examples_j = json.dumps(col.get('examples', []))
                    
                    if col_row:
                        await cursor.execute(
                            """UPDATE meta_columns SET 
                               term = %s, type = %s, description = %s, 
                               enums = %s, synonyms = %s, examples = %s, 
                               foreign_key = %s, is_primary = %s 
                               WHERE id = %s""",
                            (col['term'], col.get('type'), col.get('description'), 
                             enums_j, synonyms_j, examples_j, 
                             col.get('foreign_key'), col.get('is_primary', 0), col_row[0])
                        )
                    else:
                        await cursor.execute(
                            """INSERT INTO meta_columns 
                               (table_id, physical_name, term, type, description, enums, synonyms, examples, foreign_key, is_primary)
                               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                            (table_id, col['physical_name'], col['term'], col.get('type'), col.get('description'),
                             enums_j, synonyms_j, examples_j, col.get('foreign_key'), col.get('is_primary', 0))
                        )
                
                await conn.commit()
                # 标记为待同步
                await MetadataV2Service._mark_as_stale(dataset_id)
                
                return table_id

    # --- Metrics & Relationships ---

    @staticmethod
    async def create_metric(dataset_id: int, data: Dict[str, Any], created_by: Optional[int] = None):
        async with get_db_connection() as conn:
            async with conn.cursor() as cursor:
                # 检查是否存在 (优先用 ID，其次用 name)
                metric_id = data.get('id')
                row = None
                if metric_id:
                    await cursor.execute("SELECT id FROM meta_metrics WHERE id = %s", (metric_id,))
                    row = await cursor.fetchone()

                if not row:
                    await cursor.execute(
                        "SELECT id FROM meta_metrics WHERE dataset_id = %s AND name = %s",
                        (dataset_id, data['name'])
                    )
                    row = await cursor.fetchone()

                if row:
                    sql = """
                        UPDATE meta_metrics SET
                        name = %s, display_name = %s, description = %s, calculation_logic = %s, unit = %s
                        WHERE id = %s
                    """
                    await cursor.execute(sql, (
                        data['name'], data['display_name'], data.get('description'),
                        data['calculation_logic'], data.get('unit'), row[0]
                    ))
                else:
                    sql = """
                        INSERT INTO meta_metrics (dataset_id, name, display_name, description, calculation_logic, unit, created_by)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """
                    await cursor.execute(sql, (
                        dataset_id, data['name'], data['display_name'],
                        data.get('description'), data['calculation_logic'], data.get('unit'), created_by
                    ))
                await conn.commit()
        await MetadataV2Service._mark_as_stale(dataset_id)
    @staticmethod
    async def create_relationship(dataset_id: int, data: Dict[str, Any], created_by: Optional[int] = None):
        async with get_db_connection() as conn:
            async with conn.cursor() as cursor:
                rel_id = data.get('id')
                if rel_id:
                    sql = """
                        UPDATE meta_relationships SET
                        source_table_id = %s, target_table_id = %s, join_condition = %s,
                        join_type = %s, description = %s
                        WHERE id = %s
                    """
                    await cursor.execute(sql, (
                        data['source_table_id'], data['target_table_id'],
                        data['join_condition'], data.get('join_type', 'LEFT'), data.get('description'),
                        rel_id
                    ))
                else:
                    sql = """
                        INSERT INTO meta_relationships (source_table_id, target_table_id, join_condition, join_type, description, created_by)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """
                    await cursor.execute(sql, (
                        data['source_table_id'], data['target_table_id'],
                        data['join_condition'], data.get('join_type', 'LEFT'), data.get('description'),
                        created_by
                    ))
                await conn.commit()
        await MetadataV2Service._mark_as_stale(dataset_id)

    @staticmethod
    async def delete_metric(dataset_id: int, metric_id: int):
        async with get_db_connection() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("DELETE FROM meta_metrics WHERE id = %s", (metric_id,))
                await conn.commit()
        await MetadataV2Service._mark_as_stale(dataset_id)

    @staticmethod
    async def delete_relationship(dataset_id: int, rel_id: int):
        async with get_db_connection() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("DELETE FROM meta_relationships WHERE id = %s", (rel_id,))
                await conn.commit()
        await MetadataV2Service._mark_as_stale(dataset_id)

    @staticmethod
    async def get_dataset_usage(dataset_id: int) -> List[Dict[str, Any]]:
        """
        查询该数据集下的表被哪些 API 接口(sys_resource_meta)使用了
        """
        async with get_db_connection() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                # 1. 获取该数据集的所有物理表名和数据源
                await cursor.execute("SELECT name, data_source FROM meta_datasets WHERE id = %s", (dataset_id,))
                ds_info = await cursor.fetchone()
                if not ds_info: return []

                await cursor.execute("SELECT physical_name FROM meta_tables WHERE dataset_id = %s", (dataset_id,))
                tables = await cursor.fetchall()
                if not tables: return []

                table_names = [t['physical_name'] for t in tables]
                
                # 2. 在资源库中搜索。支持两种情况：
                # a) 直接绑定表名 (resource_mode='TABLE')
                # b) SQL 脚本包含表名 (resource_mode='SQL')
                
                # 构建表名占位符用于 SQL 匹配
                table_placeholders = ', '.join(['%s'] * len(table_names))
                like_clauses = [f"custom_sql LIKE '%%{name}%%'" for name in table_names]
                
                sql = f"""
                    SELECT id, resource_key as name, resource_name as term, data_source, updated_at, status
                    FROM sys_resource_meta
                    WHERE data_source = %s 
                      AND (
                        (resource_mode = 'TABLE' AND table_name IN ({table_placeholders}))
                        OR 
                        (resource_mode = 'SQL' AND ({' OR '.join(like_clauses)}))
                      )
                    LIMIT 100
                """
                await cursor.execute(sql, (ds_info['data_source'], *table_names))
                return await cursor.fetchall()

    @staticmethod
    async def keyword_search(data_source: str, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        核心检索逻辑：基于关键词（LIKE）在指定数据源下进行元数据检索。
        返回：包含 item_type, item_id, dataset_id 和 reason 的列表。
        """
        async with get_db_connection() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                p = f"%{query}%"
                
                # 调整 SQL：返回具体命中的实体 ID
                sql = """
                    SELECT * FROM (
                        -- 1. 匹配表
                        SELECT 'table' as item_type, t.id as item_id, t.dataset_id, 
                               CONCAT('表[', t.physical_name, ']名称、术语或描述匹配') as reason 
                        FROM meta_tables t
                        JOIN meta_datasets d ON t.dataset_id = d.id
                        WHERE d.data_source = %s AND (t.physical_name LIKE %s OR t.term LIKE %s OR t.description LIKE %s OR JSON_SEARCH(t.synonyms, 'one', %s) IS NOT NULL)
                        
                        UNION ALL
                        
                        -- 2. 匹配字段 (归属于表)
                        SELECT 'table' as item_type, t.id as item_id, t.dataset_id, 
                               CONCAT('字段[', t.physical_name, '.', c.physical_name, ']匹配') as reason 
                        FROM meta_columns c
                        JOIN meta_tables t ON c.table_id = t.id
                        JOIN meta_datasets d ON t.dataset_id = d.id
                        WHERE d.data_source = %s AND (c.physical_name LIKE %s OR c.term LIKE %s OR c.description LIKE %s OR JSON_SEARCH(c.synonyms, 'one', %s) IS NOT NULL)
                        
                        UNION ALL
                        
                        -- 3. 匹配指标
                        SELECT 'metric' as item_type, m.id as item_id, m.dataset_id, 
                               CONCAT('指标[', m.display_name, ']匹配') as reason 
                        FROM meta_metrics m
                        JOIN meta_datasets d ON m.dataset_id = d.id
                        WHERE d.data_source = %s AND (m.name LIKE %s OR m.display_name LIKE %s OR m.description LIKE %s OR m.calculation_logic LIKE %s)
                    ) as combined_results
                    LIMIT %s
                """
                
                await cursor.execute(sql, (
                    data_source, p, p, p, p,
                    data_source, p, p, p, p,
                    data_source, p, p, p, p,
                    limit
                ))
                return await cursor.fetchall()

    @staticmethod
    async def get_table_by_id(table_id: int) -> Optional[Dict[str, Any]]:
        async with get_db_connection() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute("SELECT * FROM meta_tables WHERE id = %s", (table_id,))
                table = await cursor.fetchone()
                if not table: return None
                
                if isinstance(table.get('synonyms'), str):
                    table['synonyms'] = json.loads(table['synonyms'])
                
                await cursor.execute("SELECT * FROM meta_columns WHERE table_id = %s", (table_id,))
                columns = await cursor.fetchall()
                for col in columns:
                    for field in ['enums', 'synonyms', 'examples']:
                        if isinstance(col.get(field), str):
                            col[field] = json.loads(col[field])
                table['columns'] = columns
                return table

    @staticmethod
    async def get_metric_by_id(metric_id: int) -> Optional[Dict[str, Any]]:
        async with get_db_connection() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute("SELECT * FROM meta_metrics WHERE id = %s", (metric_id,))
                return await cursor.fetchone()

    @staticmethod
    async def batch_enrich_dataset(dataset_id: int):
        """
        AI 一键自动修复：为数据集内所有缺失描述/术语的对象进行批量填充
        """
        from app.services.metadata_generator import MetadataGeneratorService
        from app.services.meta_health_service import MetaHealthService
        
        # 1. 扫描缺失项
        full_dataset = await MetadataV2Service.get_dataset_by_id(dataset_id)
        if not full_dataset: return
        
        enrich_queue = [] # 记录需要预测的对象
        
        # A. 扫描表
        for table in full_dataset.get('tables', []):
            if not table.get('term') or not table.get('description'):
                enrich_queue.append({
                    "id": table['id'], "type": "table", "name": table['physical_name'], 
                    "context": f"归属于数据集: {full_dataset.get('display_name')}"
                })
            
            # B. 扫描字段
            for col in table.get('columns', []):
                if not col.get('term') or not col.get('description'):
                    enrich_queue.append({
                        "id": col['id'], "type": "column", "name": col['physical_name'], 
                        "context": f"归属于表: {table['physical_name']} ({table.get('term', '')})"
                    })
        
        if not enrich_queue: return
        
        # 2. 调用 AI 批量预测 (分批处理防止 token 超限)
        batch_size = 30
        for i in range(0, len(enrich_queue), batch_size):
            current_batch = enrich_queue[i : i + batch_size]
            suggestions = await MetadataGeneratorService.batch_enrich(current_batch)
            
            if not suggestions or len(suggestions) != len(current_batch):
                logger.warning(f"AI Batch Enrich returned inconsistent results for dataset {dataset_id}")
                continue
                
            # 3. 写回数据库
            async with get_db_connection() as conn:
                async with conn.cursor() as cursor:
                    for obj, sug in zip(current_batch, suggestions):
                        if obj['type'] == 'table':
                            await cursor.execute(
                                "UPDATE meta_tables SET term = %s, description = %s WHERE id = %s",
                                (sug.get('term', obj['name']), sug.get('description', ''), obj['id'])
                            )
                        else:
                            await cursor.execute(
                                "UPDATE meta_columns SET term = %s, description = %s WHERE id = %s",
                                (sug.get('term', obj['name']), sug.get('description', ''), obj['id'])
                            )
                    await conn.commit()
        
        # 4. 重新标记为待同步并触发健康检查
        await MetadataV2Service._mark_as_stale(dataset_id)
        await MetaHealthService.calculate_dataset_health(dataset_id)

