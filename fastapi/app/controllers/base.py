from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from prisma import Prisma
from pydantic import BaseModel

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

class BaseController(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def get(self, db: Prisma, id: Any) -> Optional[ModelType]:
        """Get a single record by ID"""
        raise NotImplementedError
    
    async def get_multi(
        self, db: Prisma, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        """Get multiple records"""
        raise NotImplementedError
    
    async def create(self, db: Prisma, *, obj_in: CreateSchemaType) -> ModelType:
        """Create a new record"""
        raise NotImplementedError
    
    async def update(
        self,
        db: Prisma,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """Update an existing record"""
        raise NotImplementedError
    
    async def remove(self, db: Prisma, *, id: int) -> Optional[ModelType]:
        """Delete a record"""
        raise NotImplementedError