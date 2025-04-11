"""
This file contains integration tests for the rate limiter functionality.
Instead of using complex async test fixtures, we'll use a simple script 
that directly calls the API and checks the results.

This approach avoids issues with event loops and fixture management.
"""

import os
import pytest
import requests
import time
from datetime import datetime
import re

# API base URL - using the local Docker setup
API_URL = "http://localhost:8000"

def test_rate_limit_functionality():
    """
    Test that the user creation endpoint is rate limited correctly.
    This test verifies that we can create 5 users but the 6th request is rate limited.
    """
    endpoint = f"{API_URL}/api/v1/users"
    
    # Make 5 successful requests (our limit for user creation)
    for i in range(5):
        timestamp = int(time.time())
        response = requests.post(
            endpoint,
            json={
                "name": f"Rate Test User {i}",
                "email": f"ratetest{i}_{timestamp}@example.com",
                "password": "password123"
            }
        )
        assert response.status_code == 200, f"Request {i+1} failed with status {response.status_code}: {response.text}"
        assert response.json()["status"] == "success"
    
    # The 6th request should be rate limited
    timestamp = int(time.time())
    response = requests.post(
        endpoint,
        json={
            "name": "Rate Limited User",
            "email": f"ratelimited_{timestamp}@example.com",
            "password": "password123"
        }
    )
    assert response.status_code == 429, f"Expected rate limiting (429) but got {response.status_code}: {response.text}"
    
    # Print the actual response for debugging
    print(f"Rate limit response: {response.json()}")
    
    # Just check that we got a proper error response, without making assumptions about the exact structure
    error_json = response.json()
    assert error_json["status"] == "error", "Expected an error status in the response"
    
    # Non-rate-limited endpoint should still work (like healthcheck)
    response = requests.get(f"{API_URL}/internal/health")
    assert response.status_code == 200
    assert "Healthy" in response.text

def test_different_clients_separate_limits():
    """
    Test that different clients (identified by IP) have separate rate limits.
    """
    endpoint = f"{API_URL}/api/v1/users"
    
    # Create requests with different IP addresses
    headers_client1 = {"X-Forwarded-For": "192.168.1.1"}
    headers_client2 = {"X-Forwarded-For": "192.168.1.2"}
    
    # Make 5 successful requests with the first client IP
    for i in range(5):
        timestamp = int(time.time())
        response = requests.post(
            endpoint,
            headers=headers_client1,
            json={
                "name": f"Client1 User {i}",
                "email": f"client1user{i}_{timestamp}@example.com",
                "password": "password123"
            }
        )
        assert response.status_code == 200, f"Request {i+1} for client1 failed with {response.status_code}: {response.text}"
    
    # The 6th request from client1 should be rate limited
    timestamp = int(time.time())
    response = requests.post(
        endpoint,
        headers=headers_client1,
        json={
            "name": "Client1 Limited User",
            "email": f"client1limited_{timestamp}@example.com",
            "password": "password123"
        }
    )
    assert response.status_code == 429, f"Expected client1 to be rate limited, got {response.status_code}: {response.text}"
    
    # But client2 should be able to make requests (different IP = different rate limit)
    for i in range(5):
        timestamp = int(time.time())
        response = requests.post(
            endpoint,
            headers=headers_client2,
            json={
                "name": f"Client2 User {i}",
                "email": f"client2user{i}_{timestamp}@example.com",
                "password": "password123"
            }
        )
        assert response.status_code == 200, f"Request {i+1} for client2 failed with {response.status_code}: {response.text}"
    
    # The 6th request from client2 should also be rate limited
    timestamp = int(time.time())
    response = requests.post(
        endpoint,
        headers=headers_client2,
        json={
            "name": "Client2 Limited User",
            "email": f"client2limited_{timestamp}@example.com",
            "password": "password123"
        }
    )
    assert response.status_code == 429, f"Expected client2 to be rate limited, got {response.status_code}: {response.text}"

def test_rate_limit_logging():
    """
    Test that rate limit events are properly logged to the rate_limiter.log file.
    This verifies the logging functionality when rate limits are exceeded.
    """
    # Path to the log file
    log_file_path = "/app/logs/rate_limiter.log"
    
    # Get the initial log file content and size
    try:
        with open(log_file_path, 'r') as f:
            initial_log = f.read()
            initial_log_lines = len(initial_log.splitlines())
        print(f"Initial log has {initial_log_lines} lines")
    except Exception as e:
        print(f"Error reading log file: {e}")
        initial_log = ""
        initial_log_lines = 0
    
    # Now trigger a rate limit
    endpoint = f"{API_URL}/api/v1/users"
    unique_ip = f"192.168.99.{int(time.time() % 100)}"  # Generate a unique IP
    headers = {"X-Forwarded-For": unique_ip}
    
    # Make 5 successful requests with our unique IP
    for i in range(5):
        timestamp = int(time.time())
        response = requests.post(
            endpoint,
            headers=headers,
            json={
                "name": f"Log Test User {i}",
                "email": f"logtest{i}_{timestamp}@example.com",
                "password": "password123"
            }
        )
        assert response.status_code == 200, f"Request {i+1} failed with status {response.status_code}: {response.text}"
    
    # The 6th request should trigger rate limiting and logging
    timestamp = int(time.time())
    response = requests.post(
        endpoint,
        headers=headers,
        json={
            "name": "Log Limited User",
            "email": f"loglimited_{timestamp}@example.com",
            "password": "password123"
        }
    )
    assert response.status_code == 429, "Rate limit should be triggered"
    
    # Give a moment for logs to be written
    time.sleep(1)
    
    # Now check if the log file has new entries
    try:
        with open(log_file_path, 'r') as f:
            final_log = f.read()
            final_log_lines = len(final_log.splitlines())
        print(f"Final log has {final_log_lines} lines")
        
        # Check if new log entries were added
        assert final_log_lines > initial_log_lines, "New log entries should be added"
        
        # Check if the rate limit log contains our unique IP
        assert unique_ip in final_log, f"Log should contain our unique IP {unique_ip}"
        
        # Check for a rate limit warning message
        assert "Rate limit triggered" in final_log or "Rate limit exceeded" in final_log, "Log should contain rate limit warning message"
        
        # Print the new log entries for debugging
        new_lines = final_log.splitlines()[initial_log_lines:]
        print("\nNew log entries:")
        for line in new_lines:
            print(f"  {line}")
    except Exception as e:
        print(f"Error reading updated log file: {e}")
        pytest.fail(f"Failed to verify log entries: {e}") 