import redis.asyncio as redis
import redis as sync_redis
from typing import Optional
import logging

from app.config import settings

logger = logging.getLogger(__name__)

class RedisManager:
    """Redis connection manager for rate limiting"""
    
    def __init__(self, redis_url: str):
        self.redis_url = redis_url
        self._async_client: Optional[redis.Redis] = None
        self._sync_client: Optional[sync_redis.Redis] = None
    
    async def get_async_client(self) -> redis.Redis:
        """Get async Redis client"""
        if self._async_client is None:
            try:
                self._async_client = redis.from_url(
                    self.redis_url,
                    encoding="utf-8",
                    decode_responses=True,
                    retry_on_timeout=True,
                    socket_connect_timeout=5,
                    socket_timeout=5
                )
                # Test connection
                await self._async_client.ping()
                logger.info("Redis async client connected successfully")
            except Exception as e:
                logger.error(f"Failed to connect to Redis (async): {e}")
                raise
        
        return self._async_client
    
    def get_sync_client(self) -> sync_redis.Redis:
        """Get sync Redis client (for slowapi)"""
        if self._sync_client is None:
            try:
                self._sync_client = sync_redis.from_url(
                    self.redis_url,
                    encoding="utf-8",
                    decode_responses=True,
                    retry_on_timeout=True,
                    socket_connect_timeout=5,
                    socket_timeout=5
                )
                # Test connection
                self._sync_client.ping()
                logger.info("Redis sync client connected successfully")
            except Exception as e:
                logger.error(f"Failed to connect to Redis (sync): {e}")
                raise
        
        return self._sync_client
    
    async def close(self):
        """Close Redis connections"""
        if self._async_client:
            await self._async_client.close()
        if self._sync_client:
            self._sync_client.close()

# Global Redis manager
redis_manager = RedisManager(settings.REDIS_URL)