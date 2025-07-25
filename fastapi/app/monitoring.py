from slowapi.util import get_remote_address
from typing import Dict, List
import json
from datetime import datetime, timedelta

from fastapi import Request

from app.rate_limiting import get_endpoint_category, get_user_id_or_ip, get_user_type
from app.redis_client import RedisManager

class RateLimitMonitor:
    """Monitor rate limiting metrics"""
    
    def __init__(self, redis_manager: RedisManager):
        self.redis_manager = redis_manager
    
    async def get_rate_limit_stats(self, time_window: int = 3600) -> Dict:
        """Get rate limiting statistics"""
        redis_client = await self.redis_manager.get_async_client()
        
        # Get all rate limit keys
        keys = await redis_client.keys("rate_limit:*")
        
        stats = {
            "total_keys": len(keys),
            "by_user_type": {},
            "by_endpoint": {},
            "top_limited_users": [],
            "recent_limits": []
        }
        
        return stats
    
    async def log_rate_limit_hit(self, request: Request, rate_limit: str):
        """Log rate limit hit for monitoring"""
        redis_client = await self.redis_manager.get_async_client()
        
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "user_key": get_user_id_or_ip(request),
            "user_type": get_user_type(request),
            "endpoint": request.url.path,
            "method": request.method,
            "endpoint_category": get_endpoint_category(request),
            "rate_limit": rate_limit,
            "ip_address": get_remote_address(request),
            "user_agent": request.headers.get("user-agent", "")
        }
        
        # Store in Redis with expiration
        await redis_client.lpush("rate_limit_hits", json.dumps(log_entry))
        await redis_client.expire("rate_limit_hits", 86400)  # Keep for 24 hours
        
        # Keep only last 1000 entries
        await redis_client.ltrim("rate_limit_hits", 0, 999)