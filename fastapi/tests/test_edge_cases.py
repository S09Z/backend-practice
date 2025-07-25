import pytest
from httpx import AsyncClient
from prisma import Prisma

class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    @pytest.mark.asyncio
    async def test_empty_database(self, client: AsyncClient, test_db: Prisma, auth_headers: dict):
        """Test behavior with empty database."""
        # Clean up all users
        await test_db.user.delete_many()
        
        response = await client.get("/api/v1/users/", headers=auth_headers)
        # Should get 401 because the auth user no longer exists
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_zero_pagination(self, client: AsyncClient, auth_headers: dict):
        """Test pagination with zero limit."""
        response = await client.get(
            "/api/v1/users/",
            headers=auth_headers,
            params={"limit": 0, "skip": 0}
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0

    @pytest.mark.asyncio
    async def test_negative_pagination(self, client: AsyncClient, auth_headers: dict):
        """Test pagination with negative values."""
        response = await client.get(
            "/api/v1/users/",
            headers=auth_headers,
            params={"limit": -1, "skip": -1}
        )
        # Should handle gracefully, possibly with validation error
        assert response.status_code in [200, 422]

    @pytest.mark.asyncio
    async def test_very_large_pagination(self, client: AsyncClient, auth_headers: dict):
        """Test pagination with very large values."""
        response = await client.get(
            "/api/v1/users/",
            headers=auth_headers,
            params={"limit": 10000, "skip": 0}
        )
        assert response.status_code == 200
        # Should not crash even with large limit

    @pytest.mark.asyncio
    async def test_special_characters_in_search(self, client: AsyncClient):
        """Test handling of special characters in search queries."""
        special_chars = ["'", '"', ";", "--", "/*", "*/", "<", ">", "&", "%"]
        
        for char in special_chars:
            user_data = {
                "name": f"User{char}Test",
                "email": f"test{char.replace('@', 'at')}@example.com",
                "password": "password123"
            }
            
            response = await client.post("/api/v1/users/", json=user_data)
            # Should either succeed or fail gracefully
            assert response.status_code in [200, 422]