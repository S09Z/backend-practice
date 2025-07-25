import pytest
import asyncio
import time
from httpx import AsyncClient
from concurrent.futures import ThreadPoolExecutor

class TestPerformance:
    """Test performance and load handling."""
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_concurrent_user_creation(self, client: AsyncClient):
        """Test concurrent user creation."""
        async def create_user(index):
            user_data = {
                "name": f"Concurrent User {index}",
                "email": f"user{index}@concurrent.com",
                "password": "password123"
            }
            response = await client.post("/api/v1/users/", json=user_data)
            return response.status_code
        
        # Create 20 users concurrently
        start_time = time.time()
        tasks = [create_user(i) for i in range(20)]
        results = await asyncio.gather(*tasks)
        end_time = time.time()
        
        # All should succeed
        assert all(status == 200 for status in results)
        
        # Should complete in reasonable time (less than 5 seconds)
        duration = end_time - start_time
        assert duration < 5.0
        
        print(f"Created 20 users concurrently in {duration:.2f} seconds")

    @pytest.mark.performance
    @pytest.mark.asyncio 
    async def test_pagination_performance(self, client: AsyncClient, auth_headers: dict):
        """Test pagination performance."""
        # Test different page sizes
        page_sizes = [10, 50, 100]
        
        for page_size in page_sizes:
            start_time = time.time()
            response = await client.get(
                "/api/v1/users/",
                headers=auth_headers,
                params={"limit": page_size, "skip": 0}
            )
            end_time = time.time()
            
            assert response.status_code == 200
            duration = end_time - start_time
            
            # Should respond quickly (less than 1 second)
            assert duration < 1.0
            
            data = response.json()
            assert len(data) <= page_size

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_database_connection_pooling(self, client: AsyncClient):
        """Test database connection handling under load."""
        async def make_request():
            response = await client.get("/health")
            return response.status_code
        
        # Make 50 concurrent requests
        tasks = [make_request() for _ in range(50)]
        start_time = time.time()
        results = await asyncio.gather(*tasks)
        end_time = time.time()
        
        # All should succeed
        assert all(status == 200 for status in results)
        
        duration = end_time - start_time
        print(f"50 concurrent health checks completed in {duration:.2f} seconds")
