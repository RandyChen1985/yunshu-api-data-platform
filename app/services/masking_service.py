import re
import logging
import asyncio
from typing import Any, Dict, List, Optional, Union
from app.core.database import get_db_connection

logger = logging.getLogger(__name__)

class MaskingService:
    _RULES_CACHE = []
    _CACHE_TIMESTAMP = 0
    _CACHE_TTL = 300  # 5 minutes
    _LOCK = asyncio.Lock()

    @classmethod
    async def get_rules(cls):
        """获取并缓存脱敏规则"""
        import time
        now = time.time()
        if cls._RULES_CACHE and (now - cls._CACHE_TIMESTAMP < cls._CACHE_TTL):
            return cls._RULES_CACHE

        async with cls._LOCK:
            # 双重检查
            if cls._RULES_CACHE and (now - cls._CACHE_TIMESTAMP < cls._CACHE_TTL):
                return cls._RULES_CACHE
            
            try:
                async with get_db_connection() as conn:
                    async with conn.cursor() as cursor:
                        await cursor.execute(
                            "SELECT match_field, mask_type FROM sys_masking_rules WHERE is_active = 1"
                        )
                        rows = await cursor.fetchall()
                        # 将通配符 * 转换为正则
                        rules = []
                        for row in rows:
                            pattern = row[0].replace("*", ".*")
                            rules.append({
                                "pattern": re.compile(f"^{pattern}$", re.IGNORECASE),
                                "mask_type": row[1]
                            })
                        cls._RULES_CACHE = rules
                        cls._CACHE_TIMESTAMP = now
                        return rules
            except Exception as e:
                logger.error(f"Failed to load masking rules: {e}")
                return cls._RULES_CACHE or []

    @staticmethod
    def apply_mask(value: Any, mask_type: str) -> Any:
        """执行脱敏算法"""
        if value is None or not isinstance(value, str):
            return value
        
        if mask_type == "PARTIAL_3_4":
            # 13800138000 -> 138****8000
            if len(value) >= 7:
                return value[:3] + "****" + value[-4:]
            return "****"
        
        elif mask_type == "PARTIAL_4":
            # *******1234
            if len(value) >= 4:
                return "*" * (len(value) - 4) + value[-4:]
            return "****"
            
        elif mask_type == "EMAIL":
            # alice@example.com -> a***@example.com
            if "@" in value:
                prefix, domain = value.split("@", 1)
                return (prefix[0] if prefix else "") + "***@" + domain
            return "***"
            
        elif mask_type == "FULL":
            return "******"
            
        return value

    @classmethod
    async def mask_recursive(cls, data: Any, rules: List[Dict] = None) -> Any:
        """递归脱敏数据结构"""
        if rules is None:
            rules = await cls.get_rules()
        
        if not rules:
            return data

        if isinstance(data, list):
            return [await cls.mask_recursive(item, rules) for item in data]
        
        if isinstance(data, dict):
            new_dict = {}
            for key, value in data.items():
                # 检查 key 是否匹配规则
                matched_mask_type = None
                for rule in rules:
                    if rule["pattern"].match(str(key)):
                        matched_mask_type = rule["mask_type"]
                        break
                
                if matched_mask_type:
                    new_dict[key] = cls.apply_mask(value, matched_mask_type)
                else:
                    new_dict[key] = await cls.mask_recursive(value, rules)
            return new_dict
        
        return data

    @classmethod
    async def mask_list_of_lists(cls, rows: List[List[Any]], columns: List[str]) -> List[List[Any]]:
        """
        专门处理 SQL Lab 返回的二维数组结构 [[val1, val2], ...]
        配合 columns ["col1", "col2"] 使用
        """
        rules = await cls.get_rules()
        
        if not rules or not rows:
            return rows

        # 1. 预计算需要脱敏的列索引
        # mask_map: {col_index: mask_type}
        mask_map = {}
        for idx, col_name in enumerate(columns):
            for rule in rules:
                if rule["pattern"].match(str(col_name)):
                    mask_map[idx] = rule["mask_type"]
                    break
        
        if not mask_map:
            return rows

        # 2. 遍历处理
        new_rows = []
        for row in rows:
            new_row = list(row) # Shallow copy
            for idx, mask_type in mask_map.items():
                if idx < len(new_row):
                    new_row[idx] = cls.apply_mask(new_row[idx], mask_type)
            new_rows.append(new_row)
            
        return new_rows

    @staticmethod
    async def should_mask(user: dict, unmask_param: bool = False) -> bool:
        """
        三级策略判定逻辑: 用户 > 角色 > 全局
        优先级:
        1. Admin 请求 unmask=true -> False
        2. 用户策略 (ENABLE/DISABLE)
        3. 角色策略 (ENABLE/DISABLE)
        4. 全局策略 (ENABLE_DATA_MASKING)
        """
        is_admin = user.get("role") == "admin"
        
        # 0. Admin 豁免权
        if is_admin and unmask_param:
            return False

        # 1. 用户级
        user_strategy = user.get("masking_strategy", "ROLE")
        if user_strategy == "ENABLE": return True
        if user_strategy == "DISABLE": return False

        # 2. 角色级
        role_strategy = user.get("role_masking_strategy", "GLOBAL")
        if role_strategy == "ENABLE": return True
        if role_strategy == "DISABLE": return False

        # 3. 全局级
        try:
            async with get_db_connection() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(
                        "SELECT config_value FROM sys_config WHERE config_key = 'ENABLE_DATA_MASKING'"
                    )
                    row = await cursor.fetchone()
                    if row:
                        return row[0].lower() == 'true'
        except Exception as e:
            logger.error(f"Failed to check global masking config: {e}")
        
        return True # 默认开启
