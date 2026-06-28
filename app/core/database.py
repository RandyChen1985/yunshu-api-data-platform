import aiomysql
from typing import AsyncGenerator
from contextlib import asynccontextmanager
from app.core.config import settings
from tenacity import retry, stop_after_attempt, wait_exponential, before_log, retry_if_exception_type
import logging

# Configure logger
logger = logging.getLogger(__name__)

mysql_pool = None

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type(Exception)
)
async def init_db():
    """Initialize MySQL connection pool with retry"""
    global mysql_pool
    logger.info(f"🔌 Connecting to MySQL: {settings.MYSQL_USER}@{settings.MYSQL_HOST}:{settings.MYSQL_PORT}/{settings.MYSQL_DB}")
    mysql_pool = await aiomysql.create_pool(
        host=settings.MYSQL_HOST,
        port=settings.MYSQL_PORT,
        user=settings.MYSQL_USER,
        password=settings.MYSQL_PASSWORD,
        db=settings.MYSQL_DB,
        autocommit=True,
        maxsize=settings.MYSQL_POOL_SIZE
    )
    
    # Health check
    try:
        async with mysql_pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("SELECT 1")
                logger.info("✅ MySQL health check passed: SELECT 1")
    except Exception as e:
        logger.error(f"❌ MySQL health check failed: {e}")
        raise

    logger.info(f"✅ MySQL connected successfully (pool_size={settings.MYSQL_POOL_SIZE})")

async def close_db():
    """Close MySQL connection pool"""
    global mysql_pool
    if mysql_pool:
        mysql_pool.close()
        await mysql_pool.wait_closed()
        mysql_pool = None

@asynccontextmanager
async def get_db_connection():
    """Get a MySQL connection from the pool"""
    if not mysql_pool:
        await init_db()
    async with mysql_pool.acquire() as conn:
        yield conn
