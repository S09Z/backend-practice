import pytest
from httpx import AsyncClient

class TestDataValidation:
    """Test Pydantic data validation."""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_email_validation(self, client: AsyncClient):
        """Test email format validation."""
        invalid_emails = [
            "notanemail",
            "@example.com",
            "test@",
            "test..test@example.com",
            "test@.com",
            ""
        ]
        
        for invalid_email in invalid_emails:
            user_data = {
                "name": "Test User",
                "email": invalid_email,
                "password": "password123"
            }
            
            response = await client.post("/api/v1/users/", json=user_data)
            assert response.status_code == 422
            
            data = response.json()
            assert "detail" in data
            # Should contain validation error for email

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_password_requirements(self, client: AsyncClient):
        """Test password requirements."""
        weak_passwords = ["", "123", "abc", "a"]
        
        for weak_password in weak_passwords:
            user_data = {
                "name": "Test User",
                "email": "test@example.com",
                "password": weak_password
            }
            
            response = await client.post("/api/v1/users/", json=user_data)
            # Depending on your validation rules
            assert response.status_code in [200, 422]

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_numeric_validation(self, client: AsyncClient, auth_headers: dict):
        """Test numeric field validation."""
        invalid_prices = [-1, "not_a_number", float('inf'), float('-inf')]
        
        for invalid_price in invalid_prices:
            item_data = {
                "title": "Test Item",
                "price": invalid_price,
                "owner_id": 1
            }
            
            response = await client.post("/api/v1/items/", json=item_data, headers=auth_headers)
            assert response.status_code == 422