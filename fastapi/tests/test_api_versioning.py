import pytest
from httpx import AsyncClient

class TestAPIVersioning:
    """Test API versioning."""
    
    @pytest.mark.asyncio
    async def test_v1_endpoints(self, client: AsyncClient):
        """Test v1 API endpoints."""
        response = await client.get("/api/v1/users/")
        # Should get 401 (unauthorized) not 404 (not found)
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_invalid_version(self, client: AsyncClient):
        """Test invalid API version."""
        response = await client.get("/api/v999/users/")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_no_version(self, client: AsyncClient):
        """Test API access without version."""
        response = await client.get("/api/users/")
        assert response.status_code == 404