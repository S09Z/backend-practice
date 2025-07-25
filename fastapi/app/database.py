from prisma import Prisma
from contextlib import asynccontextmanager
from typing import AsyncGenerator

# Global Prisma instance
prisma = Prisma()

async def connect_database():
    """Connect to database on startup"""
    await prisma.connect()

async def disconnect_database():
    """Disconnect from database on shutdown"""
    await prisma.disconnect()

@asynccontextmanager
async def get_database() -> AsyncGenerator[Prisma, None]:
    """Get database session (context manager for transactions)"""
    async with prisma.tx() as transaction:
        yield transaction

# Dependency for FastAPI
async def get_db() -> Prisma:
    """FastAPI dependency to get database instance"""
    return prisma