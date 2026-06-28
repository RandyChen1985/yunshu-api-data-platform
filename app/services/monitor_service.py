import psutil
from typing import Dict, Any
from app.core import redis
import logging

logger = logging.getLogger(__name__)

class MonitorService:
    @staticmethod
    def get_server_stats() -> Dict[str, Any]:
        """Get system resource usage statistics"""
        # Call cpu_percent once; interval=None returns immediate value (non-blocking)
        # Note: First call might be 0.0, UI handles polling.
        cpu_percent = psutil.cpu_percent(interval=None)
        
        mem = psutil.virtual_memory()
        memory_stats = {
            "total": mem.total,
            "available": mem.available,
            "used": mem.used,
            "percent": mem.percent
        }
        
        disk = psutil.disk_usage('/')
        disk_stats = {
            "total": disk.total,
            "used": disk.used,
            "free": disk.free,
            "percent": disk.percent
        }
        
        return {
            "cpu": cpu_percent,
            "memory": memory_stats,
            "disk": disk_stats
        }

    @staticmethod
    async def get_redis_stats() -> Dict[str, Any]:
        """Get Redis internal statistics"""
        try:
            r = await redis.get_redis()
            if not r:
                return {"status": "unavailable"}
                
            info = await r.info()
            
            # Calculate Hit Rate
            keyspace_hits = info.get('keyspace_hits', 0)
            keyspace_misses = info.get('keyspace_misses', 0)
            total_ops = keyspace_hits + keyspace_misses
            hit_rate = (keyspace_hits / total_ops * 100) if total_ops > 0 else 0
            
            # Calculate Total Keys
            total_keys = 0
            for key in info:
                if key.startswith('db'):
                    val = info[key]
                    if isinstance(val, dict):
                        total_keys += val.get('keys', 0)
            
            return {
                "status": "connected",
                "version": info.get('redis_version'),
                "uptime_days": info.get('uptime_in_days'),
                "connected_clients": info.get('connected_clients'),
                "used_memory_human": info.get('used_memory_human'),
                "used_memory_rss_human": info.get('used_memory_rss_human'),
                "max_memory_human": info.get('maxmemory_human', 'Unlimited'),
                "hit_rate": round(hit_rate, 2),
                "ops_per_sec": info.get('instantaneous_ops_per_sec'),
                "total_keys": total_keys
            }
        except Exception as e:
            logger.error(f"Failed to get Redis stats: {e}")
            return {"status": "error", "error": str(e)}
