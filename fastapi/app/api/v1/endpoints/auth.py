from fastapi import APIRouter, Request, Depends, HTTPException
from prisma import Prisma

from app.main import limiter
from app.core.security import create_access_token
from app.dependencies import get_db
from app.controllers.user import user_controller
from app.schemas.user import UserCreate
from app.schemas.auth import LoginCredentials

router = APIRouter()

@router.post("/login")
@limiter.limit("10/hour")  # Very strict for login
async def login(
    request: Request,
    credentials: LoginCredentials,
    db: Prisma = Depends(get_db)
):
    """Login with rate limiting"""
    user = await user_controller.authenticate(db, email=credentials.email, password=credentials.password)
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_access_token(subject=user.id)
    return {"access_token": token, "token_type": "bearer"}

@router.post("/register")
@limiter.limit("5/hour")  # Very strict for registration
async def register(
    request: Request,
    user_data: UserCreate,
    db: Prisma = Depends(get_db)
):
    """Register with rate limiting"""
    existing_user = await user_controller.get_by_email(db, email=user_data.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    new_user = await user_controller.create(db, obj_in=user_data)
    token = create_access_token(subject=new_user.id)
    
    return {
        "user": new_user,
        "access_token": token,
        "token_type": "bearer"
    }