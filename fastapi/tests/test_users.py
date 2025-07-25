import pytest
from httpx import AsyncClient

@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_user(client: AsyncClient):
    user_data = {
        "name": "John Doe",
        "email": "john@example.com",
        "password": "testpassword123"
    }
    
    response = await client.post("/api/v1/users/", json=user_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["name"] == user_data["name"]
    assert data["email"] == user_data["email"]
    assert "id" in data
    assert "password" not in data  # Password should not be returned

@pytest.mark.asyncio
async def test_get_users(client: AsyncClient, test_user):
    # This test requires authentication, you'll need to implement login first
    # For now, this is a placeholder
    pass

@pytest.mark.unit
@pytest.mark.asyncio
async def test_duplicate_email(client: AsyncClient):
    user_data = {
        "name": "Jane Doe",
        "email": "jane@example.com",
        "password": "testpassword123"
    }
    
    # Create first user
    response1 = await client.post("/api/v1/users/", json=user_data)
    assert response1.status_code == 200
    
    # Try to create second user with same email
    response2 = await client.post("/api/v1/users/", json=user_data)
    assert response2.status_code == 400
    assert "Email already registered" in response2.json()["detail"]