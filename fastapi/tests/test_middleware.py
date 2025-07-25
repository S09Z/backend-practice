import pytest
from httpx import AsyncClient

class TestMiddleware:
    """Test custom middleware functionality."""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_cors_headers(self, client: AsyncClient):
        """Test CORS headers are present."""
        response = await client.options("/api/v1/users/")
        
        # Check CORS headers
        assert "access-control-allow-origin" in response.headers
        assert "access-control-allow-methods" in response.headers
        assert "access-control-allow-headers" in response.headers

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_request_timing(self, client: AsyncClient):
        """Test request timing middleware."""
        response = await client.get("/health")
        assert response.status_code == 200
        
        # If you have custom timing headers, test them
        # assert "X-Process-Time" in response.headers

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_security_headers(self, client: AsyncClient):
        """Test security headers."""
        response = await client.get("/")