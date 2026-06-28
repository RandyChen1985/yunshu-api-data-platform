import redis.asyncio as redis
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

redis_client = None

async def init_redis():
    global redis_client
    if settings.REDIS_ENABLE:
        logger.info(f"🔌 Connecting to Redis: {settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}")
        
        # 构造连接参数，只有密码不为空时才添加 password 参数
        redis_kwargs = {
            "host": settings.REDIS_HOST,
            "port": settings.REDIS_PORT,
            "db": settings.REDIS_DB,
            "encoding": "utf-8",
            "decode_responses": True
        }
        
        pw = settings.REDIS_PASSWORD
        if pw and pw.strip() and pw.lower() not in ["none", "null", ""]:
            logger.info("🔑 Redis: Using password authentication")
            redis_kwargs["password"] = pw
        else:
            logger.info("🔓 Redis: No password provided, using anonymous connection")
            
        redis_client = redis.Redis(**redis_kwargs)
        
        # Test connection
        await redis_client.ping()
        logger.info("✅ Redis connected successfully")
    else:
        logger.info("⚠️  Redis is disabled in settings")

async def close_redis():
    global redis_client
    if redis_client:
        await redis_client.close()
        redis_client = None

async def get_redis():
    if not redis_client and settings.REDIS_ENABLE:
        await init_redis()
    return redis_client

async def get_binary_redis():
    """Get a Redis client that returns bytes instead of strings (no decode_responses)"""
    if not settings.REDIS_ENABLE:
        return None
        
    redis_kwargs = {
        "host": settings.REDIS_HOST,
        "port": settings.REDIS_PORT,
        "db": settings.REDIS_DB,
        "decode_responses": False
    }
    
    pw = settings.REDIS_PASSWORD
    if pw and pw.strip() and pw.lower() not in ["none", "null", ""]:
        redis_kwargs["password"] = pw
        
    return redis.Redis(**redis_kwargs)
