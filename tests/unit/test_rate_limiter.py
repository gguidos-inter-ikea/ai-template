import pytest
from fastapi.testclient import TestClient
import time
from src.main import app

client = TestClient(app)

def test_user_creation_rate_limit():
    """
    Test that user creation endpoint is rate limited to 5 requests per minute.
    """
    # Make 6 requests - the first 5 should succeed, the 6th should fail
    successful_responses = 0
    rate_limited_responses = 0
    
    for i in range(6):
        response = client.post(
            "/api/v1/users",
            json={
                "name": f"Test User {i}",
                "email": f"test{i}@example.com",
                "password": "password123"
            }
        )
        
        if response.status_code == 200 and response.json()["status"] == "success":
            successful_responses += 1
        elif response.json()["error"] and "Too Many Requests" in response.json()["error"]["message"]:
            rate_limited_responses += 1
    
    # Verify that 5 requests succeeded and 1 was rate limited
    assert successful_responses == 5, f"Expected 5 successful responses, got {successful_responses}"
    assert rate_limited_responses == 1, f"Expected 1 rate-limited response, got {rate_limited_responses}"

def test_user_retrieval_rate_limit():
    """
    Test that user retrieval endpoint is rate limited to 100 requests per minute.
    """
    # Make 105 requests - the first 100 should succeed, the rest should fail
    successful_responses = 0
    rate_limited_responses = 0
    
    for i in range(105):
        response = client.get("/api/v1/users")
        
        if response.status_code == 200 and response.json()["status"] == "success":
            successful_responses += 1
        elif response.json()["error"] and "Too Many Requests" in response.json()["error"]["message"]:
            rate_limited_responses += 1
    
    # Verify that 100 requests succeeded and 5 were rate limited
    assert successful_responses == 100, f"Expected 100 successful responses, got {successful_responses}"
    assert rate_limited_responses == 5, f"Expected 5 rate-limited responses, got {rate_limited_responses}"

def test_rate_limit_reset():
    """
    Test that rate limits reset after the specified time window.
    """
    # First, use up the rate limit
    for i in range(5):
        client.post(
            "/api/v1/users",
            json={
                "name": f"Reset Test User {i}",
                "email": f"resettest{i}@example.com",
                "password": "password123"
            }
        )
    
    # Verify we're rate limited
    response = client.post(
        "/api/v1/users",
        json={
            "name": "Rate Limited User",
            "email": "ratelimited@example.com",
            "password": "password123"
        }
    )
    assert "Too Many Requests" in response.json()["error"]["message"]
    
    # Wait for rate limit to reset (60 seconds)
    # Note: In a real test, you might mock the time or use dependency injection
    # to avoid waiting the full 60 seconds
    print("Waiting for rate limit to reset... (60 seconds)")
    time.sleep(60)
    
    # Try again, should succeed now
    response = client.post(
        "/api/v1/users",
        json={
            "name": "After Reset User",
            "email": "afterreset@example.com",
            "password": "password123"
        }
    )
    assert response.status_code == 200
    assert response.json()["status"] == "success"

def test_different_endpoints_separate_limits():
    """
    Test that different endpoints have separate rate limits.
    """
    # Use up the rate limit for user creation
    for i in range(5):
        client.post(
            "/api/v1/users",
            json={
                "name": f"Separate Limit User {i}",
                "email": f"separatelimit{i}@example.com",
                "password": "password123"
            }
        )
    
    # Verify user creation is rate limited
    response = client.post(
        "/api/v1/users",
        json={
            "name": "Extra User",
            "email": "extra@example.com",
            "password": "password123"
        }
    )
    assert "Too Many Requests" in response.json()["error"]["message"]
    
    # But user retrieval should still work
    response = client.get("/api/v1/users")
    assert response.status_code == 200
    assert response.json()["status"] == "success" 