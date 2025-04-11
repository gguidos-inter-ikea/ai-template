import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI, Depends
from fastapi_limiter import FastAPILimiter
import redis.asyncio as redis
import time
import asyncio
from base.security.rate_limiter import create_rate_limiter
from src.base.config.config import settings

# Create a test-specific FastAPI app for isolation
app = FastAPI()

# Set up some rate-limited endpoints for testing
user_create_limiter = create_rate_limiter(times=3, seconds=10)  # Reduced for faster tests

@app.post("/test-user")
async def test_create_user(limit_check=Depends(user_create_limiter)):
    """Test endpoint with rate limiting."""
    return {"status": "success", "message": "User created"}

@app.get("/test-healthcheck")
async def test_healthcheck():
    """Test endpoint without rate limiting."""
    return {"status": "success", "message": "Healthy"}

@pytest.fixture(scope="module")
async def redis_client():
    """Create a Redis client for integration testing."""
    try:
        # Use the same Redis connection as the main application
        redis_url = settings.redis_url
        client = redis.from_url(redis_url, decode_responses=True)
        await client.ping()  # Check connection
        
        # Create a test-specific key prefix to avoid conflicts
        test_key_prefix = f"test_rate_limit_{int(time.time())}"
        
        # Clear any existing data with our test prefix
        keys = await client.keys(f"{test_key_prefix}*")
        if keys:
            await client.delete(*keys)
        
        yield client
        
        # Clean up
        keys = await client.keys(f"{test_key_prefix}*")
        if keys:
            await client.delete(*keys)
        
        await client.close()
    except redis.ConnectionError:
        pytest.skip("Redis server not available")

@pytest.fixture(scope="module")
async def setup_app_with_real_redis(redis_client):
    """Set up the test app with a real Redis connection."""
    # Store original Redis connection
    original_redis = FastAPILimiter._redis
    
    # Initialize with our test client
    await FastAPILimiter.init(redis_client)
    
    yield
    
    # Restore original Redis connection if there was one
    FastAPILimiter._redis = original_redis

@pytest.fixture(scope="module")
def test_client(setup_app_with_real_redis):
    """Create a test client for our app."""
    with TestClient(app) as client:
        yield client

@pytest.mark.asyncio
async def test_rate_limit_integration(test_client):
    """Test that rate limiting works with real Redis backend."""
    # Make 3 successful requests (our limit)
    for i in range(3):
        response = test_client.post("/test-user")
        assert response.status_code == 200
        assert response.json()["status"] == "success"
    
    # The 4th request should be rate limited
    response = test_client.post("/test-user")
    assert response.status_code == 429  # Too Many Requests
    
    # Non-rate-limited endpoint should still work
    response = test_client.get("/test-healthcheck")
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    
    # Wait for rate limit to reset
    await asyncio.sleep(10)
    
    # Should work again after reset
    response = test_client.post("/test-user")
    assert response.status_code == 200
    assert response.json()["status"] == "success"

@pytest.mark.asyncio
async def test_rate_limit_key_isolation(test_client, monkeypatch):
    """Test that rate limits are properly isolated by client identifier."""
    # Create a custom request object factory to simulate different clients
    original_request = TestClient.request
    client_ips = ["192.168.1.1", "192.168.1.2"]
    current_ip_index = 0
    
    def request_with_custom_ip(self, method, url, **kwargs):
        nonlocal current_ip_index
        headers = kwargs.get("headers", {})
        headers["X-Forwarded-For"] = client_ips[current_ip_index]
        kwargs["headers"] = headers
        return original_request(self, method, url, **kwargs)
    
    # Patch the request method
    monkeypatch.setattr(TestClient, "request", request_with_custom_ip)
    
    # Use up the rate limit for the first client
    for i in range(3):
        response = test_client.post("/test-user")
        assert response.status_code == 200
    
    # Verify first client is rate limited
    response = test_client.post("/test-user")
    assert response.status_code == 429
    
    # Switch to second client
    current_ip_index = 1
    
    # Second client should not be rate limited
    for i in range(3):
        response = test_client.post("/test-user")
        assert response.status_code == 200
    
    # Now second client should be rate limited
    response = test_client.post("/test-user")
    assert response.status_code == 429
    
    # First client is still rate limited
    current_ip_index = 0
    response = test_client.post("/test-user")
    assert response.status_code == 429 