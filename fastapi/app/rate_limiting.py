from slowapi.util import get_remote_address
from fastapi import Request
from typing import Callable, Optional
import re

from app.config import Settings

def get_user_id_or_ip(request: Request) -> str:
    """
    Get user ID if authenticated, otherwise use IP address
    This provides per-user rate limiting for authenticated users
    and per-IP for anonymous users
    """
    # Try to get user from request state (set by auth middleware)
    user = getattr(request.state, 'user', None)
    if user and hasattr(user, 'id'):
        return f"user:{user.id}"
    
    # Try to get user from dependency injection
    if hasattr(request, 'user') and request.user:
        return f"user:{request.user.id}"
    
    # Fall back to IP address
    ip_address = get_remote_address(request)
    return f"ip:{ip_address}"

def get_user_type(request: Request) -> str:
    """Determine user type for different rate limits"""
    user = getattr(request.state, 'user', None) or getattr(request, 'user', None)
    
    if not user:
        return "anonymous"
    
    # Check user role/type
    if hasattr(user, 'role'):
        if user.role == "admin" or user.role == "premium":
            return "premium"
        elif user.role == "user":
            return "authenticated"
    
    # Default for authenticated users
    return "authenticated"

def get_endpoint_category(request: Request) -> str:
    """Categorize endpoint for different rate limits"""
    path = request.url.path
    method = request.method
    
    # Health check endpoints
    if path in ["/health", "/", "/docs", "/redoc", "/openapi.json"]:
        return "health"
    
    # Authentication endpoints
    if "/auth/" in path:
        if "login" in path:
            return "auth_login"
        elif "register" in path or "signup" in path:
            return "auth_register"
        return "auth"
    
    # API endpoints
    if path.startswith("/api/"):
        if method in ["GET", "HEAD", "OPTIONS"]:
            return "api_read"
        elif method in ["POST", "PUT", "PATCH", "DELETE"]:
            return "api_write"
    
    return "default"

def is_whitelisted_ip(request: Request) -> bool:
    """Check if IP is whitelisted"""
    ip_address = get_remote_address(request)
    return ip_address in Settings.RATE_LIMIT_WHITELIST

def get_rate_limit_for_request(request: Request) -> str:
    """Get appropriate rate limit for the request"""
    if not Settings.RATE_LIMIT_ENABLED:
        return "10000/minute"  # Very high limit when disabled
    
    if is_whitelisted_ip(request):
        return "10000/minute"  # High limit for whitelisted IPs
    
    user_type = get_user_type(request)
    endpoint_category = get_endpoint_category(request)
    
    # Get user-type specific limits first
    user_limits = Settings.USER_TYPE_RATE_LIMITS.get(user_type, {})
    if endpoint_category in user_limits:
        return user_limits[endpoint_category]
    
    # Fall back to general endpoint limits
    if endpoint_category in Settings.RATE_LIMITS:
        return Settings.RATE_LIMITS[endpoint_category]
    
    # Default limit
    return Settings.DEFAULT_RATE_LIMIT