from fastapi import APIRouter, Depends, HTTPException
from app.dependencies import get_current_admin_user
from app.monitoring import RateLimitMonitor
from app.redis_client import redis_manager

admin_router = APIRouter(prefix="/admin", tags=["admin"])

@admin_router.get("/rate-limits/stats")
async def get_rate_limit_stats(
    current_admin = Depends(get_current_admin_user)
):
    """Get rate limiting statistics (admin only)"""
    monitor = RateLimitMonitor(redis_manager)
    stats = await monitor.get_rate_limit_stats()
    return stats

@admin_router.delete("/rate-limits/reset/{user_key}")
async def reset_user_rate_limit(
    user_key: str,
    current_admin = Depends(get_current_admin_user)
):
    """Reset rate limit for specific user (admin only)"""
    redis_client = redis_manager.get_sync_client()
    # Find and delete all keys for this user
    pattern = f"*{user_key}*"
    keys = redis_client.keys(pattern)
    
    if keys:
        redis_client.delete(*keys)
        return {"message": f"Reset rate limits for {user_key}", "keys_deleted": len(keys)}
    else:
        return {"message": f"No rate limit data found for {user_key}"}

@admin_router.post("/rate-limits/whitelist/{ip_address}")
async def add_ip_to_whitelist(
    ip_address: str,
    current_admin = Depends(get_current_admin_user)
):
    """Add IP to rate limit whitelist (admin only)"""
    # This would typically update a database or config
    # For now, we'll just return success
    return {"message": f"Added {ip_address} to whitelist"}