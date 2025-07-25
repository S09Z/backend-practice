from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ItemBase(BaseModel):
    title: str
    description: Optional[str] = None
    price: float
    is_available: Optional[bool] = True

class ItemCreate(ItemBase):
    owner_id: int

class ItemUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    is_available: Optional[bool] = None

class ItemInDB(ItemBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime

class ItemResponse(ItemInDB):
    pass

class ItemWithOwner(ItemResponse):
    owner: 'UserResponse'

# Import at the end to avoid circular imports
from app.schemas.user import UserResponse
ItemWithOwner.model_rebuild()