import logging
import json
from typing import Dict, Any, List
from app.core.database import get_db_connection

logger = logging.getLogger(__name__)

class MetaHealthService:
    """Service for calculating AI Readiness Score for metadata datasets"""

    @staticmethod
    async def calculate_dataset_health(dataset_id: int) -> Dict[str, Any]:
        """扫描数据集元数据并计算得分"""
        async with get_db_connection() as conn:
            import aiomysql
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                # 1. 获取基础数据
                await cursor.execute("SELECT * FROM meta_datasets WHERE id = %s", (dataset_id,))
                dataset = await cursor.fetchone()
                if not dataset:
                    return {"score": 0, "report": {"error": "Dataset not found"}}

                await cursor.execute("SELECT * FROM meta_tables WHERE dataset_id = %s", (dataset_id,))
                tables = await cursor.fetchall()
                table_ids = [t['id'] for t in tables]

                columns = []
                if table_ids:
                    placeholders = ', '.join(['%s'] * len(table_ids))
                    await cursor.execute(f"SELECT * FROM meta_columns WHERE table_id IN ({placeholders})", tuple(table_ids))
                    columns = await cursor.fetchall()

                await cursor.execute("SELECT * FROM meta_metrics WHERE dataset_id = %s", (dataset_id,))
                metrics = await cursor.fetchall()

                await cursor.execute("""
                    SELECT * FROM meta_relationships 
                    WHERE source_table_id IN (SELECT id FROM meta_tables WHERE dataset_id = %s)
                """, (dataset_id,))
                relationships = await cursor.fetchall()

        # 2. 评分引擎逻辑
        score = 0
        issues = []
        
        # A. 数据集级别 (10分)
        if dataset.get('description'):
            score += 10
        else:
            issues.append({"level": "dataset", "msg": "数据集缺少业务背景描述", "impact": 10})

        # B. 表级别 (20分)
        if not tables:
            issues.append({"level": "table", "msg": "未导入任何物理表", "impact": 20})
        else:
            tables_with_term = [t for t in tables if t.get('term')]
            tables_with_desc = [t for t in tables if t.get('description')]
            
            term_score = (len(tables_with_term) / len(tables)) * 10
            desc_score = (len(tables_with_desc) / len(tables)) * 10
            score += (term_score + desc_score)
            
            if len(tables_with_term) < len(tables):
                issues.append({"level": "table", "msg": f"部分表({len(tables)-len(tables_with_term)}个)缺失业务术语", "impact": 5})

        # C. 字段级别 (40分)
        if not columns:
            issues.append({"level": "column", "msg": "表内无字段元数据", "impact": 40})
        else:
            cols_with_term = [c for c in columns if c.get('term')]
            cols_with_desc = [c for c in columns if c.get('description')]
            
            c_term_score = (len(cols_with_term) / len(columns)) * 20
            c_desc_score = (len(cols_with_desc) / len(columns)) * 20
            score += (c_term_score + c_desc_score)
            
            if len(cols_with_term) < len(columns):
                issues.append({"level": "column", "msg": "大量字段缺失业务术语，AI 无法理解查询目标", "impact": 15})

        # D. 指标级别 (20分)
        if not metrics:
            issues.append({"level": "metric", "msg": "未定义任何业务指标，复杂聚合将无法处理", "impact": 20})
        else:
            score += 10 # 只要有指标就给10分底分
            metrics_complete = [m for m in metrics if m.get('calculation_logic') and m.get('description')]
            m_comp_score = (len(metrics_complete) / len(metrics)) * 10
            score += m_comp_score

        # E. 关系级别 (10分)
        if relationships:
            score += 10
        else:
            issues.append({"level": "relationship", "msg": "未定义多表关联关系，AI 无法进行多维分析", "impact": 10})

        final_score = int(min(max(score, 0), 100))
        
        report = {
            "dataset_id": dataset_id,
            "check_time": str(logging.Formatter().formatTime(logging.makeLogRecord({}))), # 简易时间戳
            "issues": issues,
            "stats": {
                "tables": len(tables),
                "columns": len(columns),
                "metrics": len(metrics),
                "relationships": len(relationships)
            }
        }

        # 3. 异步更新数据库分数 (假设字段已由用户手动增加)
        try:
            async with get_db_connection() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(
                        "UPDATE meta_datasets SET health_score = %s, health_report = %s WHERE id = %s",
                        (final_score, json.dumps(report), dataset_id)
                    )
                    await conn.commit()
        except Exception as e:
            logger.error(f"Failed to save health score for dataset {dataset_id}: {e}")

        return {"score": final_score, "report": report}
