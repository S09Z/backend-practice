from typing import List, Optional, Dict, Any, Union
from prisma import Prisma
from prisma.models import User

from app.controllers.base import BaseController
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password

class UserController(BaseController[User, UserCreate, UserUpdate]):
    
    async def get(self, db: Prisma, id: int) -> Optional[User]:
        return await db.user.find_unique(where={"id": id})
    
    async def get_by_email(self, db: Prisma, *, email: str) -> Optional[User]:
        return await db.user.find_unique(where={"email": email})
    
    async def get_multi(self, db: Prisma, *, skip: int = 0, limit: int = 100) -> List[User]:
        return await db.user.find_many(skip=skip, take=limit)
    
    async def create(self, db: Prisma, *, obj_in: UserCreate) -> User:
        hashed_password = get_password_hash(obj_in.password)
        return await db.user.create(
            data={
                "email": obj_in.email,
                "name": obj_in.name,
                "password": hashed_password,
                "is_active": obj_in.is_active,
            }
        )
    
    async def update(
        self,
        db: Prisma,
        *,
        db_obj: User,
        obj_in: Union[UserUpdate, Dict[str, Any]]
    ) -> User:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        
        # Hash password if provided
        if "password" in update_data:
            update_data["password"] = get_password_hash(update_data["password"])
        
        return await db.user.update(
            where={"id": db_obj.id},
            data=update_data
        )
    
    async def remove(self, db: Prisma, *, id: int) -> Optional[User]:
        return await db.user.delete(where={"id": id})
    
    async def authenticate(self, db: Prisma, *, email: str, password: str) -> Optional[User]:
        user = await self.get_by_email(db, email=email)
        if not user:
            return None
        if not verify_password(password, user.password):
            return None
        return user
    
    async def is_active(self, user: User) -> bool:
        return user.is_active

user_controller = UserController(User)