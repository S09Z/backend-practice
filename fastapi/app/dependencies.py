from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from prisma import Prisma
from prisma.models import User
from typing import Optional
from jose import JWTError, jwt
import logging

from app.database import get_db
from app.core.security import verify_token
from app.config import settings

logger = logging.getLogger(__name__)

# Security scheme
security = HTTPBearer(auto_error=False)

# =========================
# Core Authentication Dependencies (USED)
# =========================

async def get_current_user_optional(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Prisma = Depends(get_db)
) -> Optional[User]:
    """
    Get current user if authenticated, return None if not
    USED IN: Rate limiting, optional auth endpoints
    """
    if not credentials:
        return None
    
    try:
        user = await verify_token(credentials.credentials, db)
        if user:
            # Store user in request state for rate limiting
            request.state.user = user
        return user
    except Exception as e:
        logger.warning(f"Token verification failed: {e}")
        return None

async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Prisma = Depends(get_db)
) -> User:
    """
    Get current authenticated user (required)
    USED IN: Protected endpoints (users, items, etc.)
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        user = await verify_token(credentials.credentials, db)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Inactive user account",
            )
        
        # Store user in request state for rate limiting
        request.state.user = user
        return user
        
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_admin_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current user and verify admin privileges
    USED IN: Admin endpoints only (/admin/rate-limits/stats, etc.)
    """
    # Check if user has admin role
    user_role = getattr(current_user, 'role', 'user')
    if user_role != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user

# =========================
# Rate Limiting Helper (USED)
# =========================

def get_user_type_from_request(request: Request) -> str:
    """
    Get user type from request state for rate limiting
    USED IN: Rate limiting logic
    """
    user = getattr(request.state, 'user', None)
    if not user:
        return "anonymous"
    
    role = getattr(user, 'role', 'user')
    if role == 'admin' or role == 'premium':
        return "premium"
    elif role == 'user':
        return "authenticated"
    else:
        return "authenticated"

# =========================
# Simplified Rate Limiting Functions (USED)
# =========================

from slowapi.util import get_remote_address

def get_user_id_or_ip(request: Request) -> str:
    """
    Get user ID if authenticated, otherwise use IP address
    USED IN: slowapi key function
    """
    user = getattr(request.state, 'user', None)
    if user and hasattr(user, 'id'):
        return f"user:{user.id}"
    
    ip_address = get_remote_address(request)
    return f"ip:{ip_address}"

def get_endpoint_category(request: Request) -> str:
    """
    Categorize endpoint for different rate limits
    USED IN: Rate limiting configuration
    """
    path = request.url.path
    method = request.method
    
    # Health check endpoints
    if path in ["/health", "/", "/docs", "/redoc", "/openapi.json"]:
        return "health"
    
    # Authentication endpoints
    if "/auth/" in path:
        if "login" in path:
            return "auth_login"
        elif "register" in path:
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
    """
    Check if IP is whitelisted
    USED IN: Rate limiting bypass
    """
    ip_address = get_remote_address(request)
    whitelist = getattr(settings, 'RATE_LIMIT_WHITELIST', ['127.0.0.1', '::1'])
    return ip_address in whitelist

def get_rate_limit_for_request(request: Request) -> str:
    """
    Get appropriate rate limit for the request
    USED IN: Dynamic rate limiting
    """
    if not getattr(settings, 'RATE_LIMIT_ENABLED', True):
        return "10000/minute"
    
    if is_whitelisted_ip(request):
        return "10000/minute"
    
    user_type = get_user_type_from_request(request)
    endpoint_category = get_endpoint_category(request)
    
    # Rate limits configuration
    rate_limits = {
        # Anonymous users
        "anonymous": {
            "default": "50/hour",
            "auth_login": "10/hour",
            "auth_register": "3/hour",
            "api_read": "100/hour",
            "api_write": "20/hour",
            "health": "1000/minute"
        },
        # Authenticated users
        "authenticated": {
            "default": "1000/hour",
            "api_read": "5000/hour",
            "api_write": "1000/hour",
            "health": "1000/minute"
        },
        # Premium users (admin, premium role)
        "premium": {
            "default": "10000/hour",
            "api_read": "50000/hour",
            "api_write": "10000/hour",
            "health": "1000/minute"
        }
    }
    
    # Get rate limit for user type and endpoint
    user_limits = rate_limits.get(user_type, rate_limits["anonymous"])
    return user_limits.get(endpoint_category, user_limits.get("default", "100/hour"))
