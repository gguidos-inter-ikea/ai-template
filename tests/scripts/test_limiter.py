#!/usr/bin/env python
"""
Simple script to test if FastAPILimiter is initialized.
"""
import requests
import json

# API base URL
API_URL = "http://localhost:8000"

def test_rate_limiter():
    """
    Test if the rate limiter is working by making multiple requests.
    """
    # First, make a request to a non-rate-limited endpoint
    print("Testing health endpoint (not rate limited)...")
    response = requests.get(f"{API_URL}/internal/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:100]}...")
    print("-" * 50)
    
    # Now test the rate-limited endpoint
    endpoint = f"{API_URL}/api/v1/users"
    client_ip = "192.168.99.999"  # Use a unique IP
    headers = {"X-Forwarded-For": client_ip}
    
    print(f"Testing user creation endpoint with IP {client_ip}...")
    
    # Make 6 requests - the 6th should be rate limited if working correctly
    for i in range(6):
        timestamp = int(requests.get("http://worldtimeapi.org/api/timezone/Etc/UTC").json()["unixtime"])
        response = requests.post(
            endpoint,
            headers=headers,
            json={
                "name": f"Test User {i}",
                "email": f"testuser{i}_{timestamp}@example.com",
                "password": "password123"
            }
        )
        
        print(f"Request {i+1}: Status {response.status_code}")
        print(f"Response: {response.text[:100]}...")
        
        # If we get a 429, the rate limiter is working
        if response.status_code == 429:
            print("✅ Rate limiter is working! Request was rate limited.")
            break
    
    # If we made all 6 requests without getting a 429, the rate limiter is not working
    if i == 5 and response.status_code != 429:
        print("❌ Rate limiter is NOT working! All requests succeeded.")

if __name__ == "__main__":
    test_rate_limiter() 