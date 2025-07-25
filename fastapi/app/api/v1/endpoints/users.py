from fastapi import APIRouter, Depends, HTTPException
from prisma import Prisma
from typing import List

from app.dependencies import get_db, get_current_user
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.controllers.user import user_controller
from prisma.models import User

router = APIRouter()

@router.post("/", response_model=UserResponse)
async def create_user(
    user_in: UserCreate,
    db: Prisma = Depends(get_db)
):
    # Check if user already exists
    existing_user = await user_controller.get_by_email(db, email=user_in.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user = await user_controller.create(db, obj_in=user_in)
    return user

@router.get("/", response_model=List[UserResponse])
async def read_users(
    skip: int = 0,
    limit: int = 100,
    db: Prisma = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    users = await user_controller.get_multi(db, skip=skip, limit=limit)
    return users

@router.get("/{user_id}", response_model=UserResponse)
async def read_user(
    user_id: int,
    db: Prisma = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user = await user_controller.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_in: UserUpdate,
    db: Prisma = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user = await user_controller.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user = await user_controller.update(db, db_obj=user, obj_in=user_in)
    return user

@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    db: Prisma = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user = await user_controller.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    await user_controller.remove(db, id=user_id)
    return {"message": "User deleted successfully"}