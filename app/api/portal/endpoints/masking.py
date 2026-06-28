from fastapi import APIRouter, Depends, HTTPException, Query, Body
from typing import List, Optional
from pydantic import BaseModel, Field
from app.core.dependencies import require_admin
from app.core.database import get_db_connection
from app.services.masking_service import MaskingService

router = APIRouter()

class MaskingRuleBase(BaseModel):
    rule_name: str
    match_field: str
    mask_type: str
    is_active: int = 1
    description: Optional[str] = None

class MaskingRuleCreate(MaskingRuleBase):
    pass

class MaskingRuleUpdate(BaseModel):
    rule_name: Optional[str] = None
    match_field: Optional[str] = None
    mask_type: Optional[str] = None
    is_active: Optional[int] = None
    description: Optional[str] = None

@router.get("/rules")
async def get_masking_rules(user=Depends(require_admin)):
    """获取所有脱敏规则"""
    async with get_db_connection() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("SELECT * FROM sys_masking_rules ORDER BY id DESC")
            rows = await cursor.fetchall()
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in rows]

@router.post("/rules")
async def create_masking_rule(rule: MaskingRuleCreate, user=Depends(require_admin)):
    """创建脱敏规则"""
    async with get_db_connection() as conn:
        async with conn.cursor() as cursor:
            try:
                await cursor.execute(
                    """INSERT INTO sys_masking_rules 
                       (rule_name, match_field, mask_type, is_active, description) 
                       VALUES (%s, %s, %s, %s, %s)""",
                    (rule.rule_name, rule.match_field, rule.mask_type, rule.is_active, rule.description)
                )
                await conn.commit()
                # 刷新缓存
                MaskingService._RULES_CACHE = []
                return {"status": "success", "id": cursor.lastrowid}
            except Exception as e:
                await conn.rollback()
                raise HTTPException(status_code=400, detail=str(e))

@router.put("/rules/{rule_id}")
async def update_masking_rule(rule_id: int, rule: MaskingRuleUpdate, user=Depends(require_admin)):
    """更新脱敏规则"""
    async with get_db_connection() as conn:
        async with conn.cursor() as cursor:
            update_data = rule.dict(exclude_unset=True)
            if not update_data:
                return {"status": "success"}
            
            fields = ", ".join([f"{k} = %s" for k in update_data.keys()])
            params = list(update_data.values()) + [rule_id]
            
            await cursor.execute(f"UPDATE sys_masking_rules SET {fields} WHERE id = %s", params)
            await conn.commit()
            MaskingService._RULES_CACHE = []
            return {"status": "success"}

@router.delete("/rules/{rule_id}")
async def delete_masking_rule(rule_id: int, user=Depends(require_admin)):
    """删除脱敏规则"""
    async with get_db_connection() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("DELETE FROM sys_masking_rules WHERE id = %s", (rule_id,))
            await conn.commit()
            MaskingService._RULES_CACHE = []
            return {"status": "success"}

@router.get("/config")
async def get_masking_config(user=Depends(require_admin)):
    """获取脱敏全局配置"""
    async with get_db_connection() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(
                "SELECT config_value FROM sys_config WHERE config_key = 'ENABLE_DATA_MASKING'"
            )
            row = await cursor.fetchone()
            return {"enabled": row[0].lower() == 'true' if row else True}

@router.post("/config")
async def update_masking_config(enabled: bool = Body(..., embed=True), user=Depends(require_admin)):
    """更新脱敏全局配置"""
    async with get_db_connection() as conn:
        async with conn.cursor() as cursor:
            val = 'true' if enabled else 'false'
            await cursor.execute(
                "UPDATE sys_config SET config_value = %s WHERE config_key = 'ENABLE_DATA_MASKING'",
                (val,)
            )
            await conn.commit()
            return {"status": "success"}
