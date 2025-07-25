import pytest
from httpx import AsyncClient

class TestErrorHandling:
    """Test error handling and edge cases."""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_invalid_json(self, client: AsyncClient):
        """Test handling of invalid JSON."""
        response = await client.post(
            "/api/v1/users/",
            content="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_missing_content_type(self, client: AsyncClient):
        """Test handling of missing content type."""
        response = await client.post("/api/v1/users/", content='{"name": "test"}')
        # Should still work as FastAPI is forgiving
        assert response.status_code in [422, 400]

    @pytest.mark.asyncio
    async def test_sql_injection_attempt(self, client: AsyncClient):
        """Test protection against SQL injection."""
        malicious_data = {
            "name": "'; DROP TABLE users; --",
            "email": "hack@example.com",
            "password": "password123"
        }
        
        response = await client.post("/api/v1/users/", json=malicious_data)
        # Should either succeed (properly escaped) or fail validation
        assert response.status_code in [200, 422]
        
        # Verify users table still exists by trying to fetch users
        # (This would fail if SQL injection worked)
        users_response = await client.get("/api/v1/users/")
        # Should get 401 (unauthorized) not 500 (server error)
        assert users_response.status_code == 401

    @pytest.mark.asyncio
    async def test_extremely_long_input(self, client: AsyncClient):
        """Test handling of extremely long input."""
        long_string = "x" * 10000
        user_data = {
            "name": long_string,
            "email": "long@example.com",
            "password": "password123"
        }
        
        response = await client.post("/api/v1/users/", json=user_data)
        # Should handle gracefully with validation error
        assert response.status_code == 422

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_unicode_handling(self, client: AsyncClient):
        """Test Unicode character handling."""
        unicode_data = {
            "name": "用户测试 🚀 ñáéíóú",
            "email": "unicode@example.com",
            "password": "pássword123"
        }
        
        response = await client.post("/api/v1/users/", json=unicode_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["name"] == unicode_data["name"]