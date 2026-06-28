import logging
import json
from typing import Optional, Dict, Any
from app.core.database import get_db_connection
from app.core.redis import get_redis

logger = logging.getLogger(__name__)

class SystemService:
    """
    Service for handling system-wide configurations and maintenance tasks.
    """
    CACHE_PREFIX = "yunshu:config:"
    _local_cache = {}
    _last_refresh = 0
    REFRESH_INTERVAL = 60 # 1 minute local cache fallback

    @classmethod
    async def get_config(cls, key: str, default: Any = None) -> Any:
        """
        Get a system configuration value by key.
        Order: Redis -> Database (and cache back to Redis)
        """
        redis_key = f"{cls.CACHE_PREFIX}{key}"
        
        # 1. Try Redis
        try:
            r = await get_redis()
            if r:
                val = await r.get(redis_key)
                if val is not None:
                    return val
        except Exception as e:
            logger.warning(f"Failed to read config from Redis: {e}")

        # 2. Try Database
        try:
            async with get_db_connection() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(
                        "SELECT config_value FROM sys_config WHERE config_key = %s",
                        (key,)
                    )
                    row = await cursor.fetchone()
                    if row:
                        value = row[0]
                        # Cache back to Redis (Ensure value is not None)
                        if r and value is not None:
                            await r.setex(redis_key, 3600, str(value))
                        return value
        except Exception as e:
            logger.error(f"Failed to read config from DB: {e}")

        return default

    @classmethod
    async def get_int_config(cls, key: str, default: int = 0) -> int:
        val = await cls.get_config(key)
        try:
            return int(val) if val is not None else default
        except (ValueError, TypeError):
            return default

    @classmethod
    async def get_bool_config(cls, key: str, default: bool = False) -> bool:
        val = await cls.get_config(key)
        if val is None:
            return default
        return str(val).lower() in ('true', '1', 'yes', 'on')

    @classmethod
    async def set_config(cls, key: str, value: Any, group: str = 'system'):
        """
        Set a system configuration value and invalidate cache.
        """
        async with get_db_connection() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    """
                    INSERT INTO sys_config (config_key, config_value, config_group)
                    VALUES (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE config_value = VALUES(config_value)
                    """,
                    (key, str(value), group)
                )
                await conn.commit()
        
        # Invalidate Redis
        try:
            r = await get_redis()
            if r:
                await r.delete(f"{cls.CACHE_PREFIX}{key}")
        except:
            pass

    @classmethod
    async def get_all_configs(cls) -> Dict[str, str]:
        """Fetch all configurations from DB"""
        configs = {}
        async with get_db_connection() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("SELECT config_key, config_value FROM sys_config")
                rows = await cursor.fetchall()
                for row in rows:
                    configs[row[0]] = row[1]
        return configs
