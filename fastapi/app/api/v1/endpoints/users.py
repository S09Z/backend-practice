from fastapi import APIRouter, Depends, Request, HTTPException
from prisma import Prisma
from prisma.models import User
from typing import List, Optional
from slowapi import Limiter

from app.dependencies import get_current_user, get_current_user_optional, get_db
from app.schemas.user import UserCreate, UserResponse
from app.controllers.user import user_controller

# Get limiter from main app
from app.main import limiter

router = APIRouter()

@router.get("/", response_model=List[UserResponse])
@limiter.limit("100/hour")  # This will be overridden by dynamic rate limiting
async def get_users(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    db: Prisma = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Get users with rate limiting"""
    users = await user_controller.get_multi(db, skip=skip, limit=limit)
    return users

@router.post("/", response_model=UserResponse)
@limiter.limit("10/hour")  # Strict limit for user creation
async def create_user(
    request: Request,
    user: UserCreate,
    db: Prisma = Depends(get_db)
):
    """Create user"""
    existing_user = await user_controller.get_by_email(db, email=user.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    new_user = await user_controller.create(db, obj_in=user)
    return new_user

@router.get("/{user_id}", response_model=UserResponse)
@limiter.limit("500/hour")
async def get_user(
    user_id: int,
    request: Request,
    db: Prisma = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get specific user"""
    user = await user_controller.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user