import pytest
import asyncio
from httpx import AsyncClient
from prisma import Prisma

from app.main import app

# Test database URL (use a separate test database)
TEST_DATABASE_URL = "sqlite:file:./test.db"

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def test_db():
    # Use a separate Prisma instance for testing
    test_prisma = Prisma(datasource={"url": TEST_DATABASE_URL})
    await test_prisma.connect()
    
    # Reset database for testing
    await test_prisma._execute_raw("PRAGMA foreign_keys = OFF")
    await test_prisma.user.delete_many()
    await test_prisma.item.delete_many()
    await test_prisma.auth_token.delete_many()
    await test_prisma._execute_raw("PRAGMA foreign_keys = ON")
    
    yield test_prisma
    await test_prisma.disconnect()

@pytest.fixture
async def client(test_db):
    # Override the get_db dependency for testing
    from app.database import get_db
    
    async def override_get_db():
        return test_db
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    # Clean up
    app.dependency_overrides.clear()

@pytest.fixture
async def test_user(test_db):
    """Create a test user"""
    from app.controllers.user import user_controller
    from app.schemas.user import UserCreate
    
    user_data = UserCreate(
        name="Test User",
        email="test@example.com",
        password="testpassword"
    )
    
    user = await user_controller.create(test_db, obj_in=user_data)
    return user