from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# Base schemas
class UserBase(BaseModel):
    email: EmailStr
    name: str
    is_active: Optional[bool] = True

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None

class UserInDB(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

class UserResponse(UserInDB):
    pass

# For including related data
class UserWithItems(UserResponse):
    items: List['ItemResponse'] = []

# Import at the end to avoid circular imports
from app.schemas.item import ItemResponse
UserWithItems.model_rebuild()