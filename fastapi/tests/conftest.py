import pytest
import pytest_asyncio
import asyncio
import os
from httpx import AsyncClient, ASGITransport
from prisma import Prisma

from app.main import app

# Use the same PostgreSQL database for tests (you could create a separate test database)
TEST_DATABASE_URL = os.getenv("DATABASE_URL")

@pytest.fixture(scope="session")
def event_loop():
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture
async def test_db():
    # Set test database URL as environment variable
    os.environ["DATABASE_URL"] = TEST_DATABASE_URL
    
    # Use a separate Prisma instance for testing
    test_prisma = Prisma()
    await test_prisma.connect()
    
    # Reset database for testing - only clear existing models
    await test_prisma.user.delete_many()
    
    yield test_prisma
    await test_prisma.disconnect()
    
    # Clean up - remove any test records if needed
    pass

@pytest_asyncio.fixture
async def client(test_db):
    # Override the get_db dependency for testing
    from app.database import get_db
    
    async def override_get_db():
        return test_db
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    
    # Clean up
    app.dependency_overrides.clear()

@pytest_asyncio.fixture
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

@pytest_asyncio.fixture
async def auth_headers(test_user):
    """Create authentication headers for a test user"""
    from app.core.security import create_access_token
    
    access_token = create_access_token(subject=test_user.id)
    return {"Authorization": f"Bearer {access_token}"}