#!/usr/bin/env python3
"""
Test script to demonstrate rate limiting functionality and logging.
This script sends multiple requests to the API to trigger rate limiting
and then displays the rate limit logs.
"""
import requests
import time
import json
import sys
import os
from datetime import datetime

# Configuration
API_URL = "http://localhost:8000/api/v1"
USER_ENDPOINT = f"{API_URL}/users"
NUM_REQUESTS = 10
REQUEST_DELAY = 0.1  # seconds between requests

def create_user(index):
    """Create a test user with the given index"""
    timestamp = int(time.time())
    data = {
        "name": f"Test User {timestamp}-{index}",
        "email": f"test{timestamp}_{index}@example.com",
        "password": "password123"
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(USER_ENDPOINT, json=data, headers=headers)
        return response
    except Exception as e:
        print(f"Error making request: {e}")
        return None

def print_separator():
    """Print a separator line"""
    print("-" * 80)

def main():
    """Main function to run the test"""
    print("Rate Limit Testing Script")
    print_separator()
    print(f"Target: {USER_ENDPOINT}")
    print(f"Sending {NUM_REQUESTS} requests with {REQUEST_DELAY}s delay between them")
    print_separator()
    
    # Track responses
    responses = []
    
    # Send requests
    for i in range(1, NUM_REQUESTS + 1):
        print(f"Request {i}/{NUM_REQUESTS}...", end="", flush=True)
        start_time = time.time()
        response = create_user(i)
        duration = time.time() - start_time
        
        if response:
            status_code = response.status_code
            try:
                response_data = response.json()
            except:
                response_data = {"error": "Could not parse JSON response"}
            
            responses.append({
                "index": i,
                "status_code": status_code,
                "duration": duration,
                "data": response_data
            })
            
            status_indicator = "✓" if status_code == 200 else "✗"
            print(f" {status_indicator} [{status_code}] in {duration:.2f}s")
        else:
            print(" ✗ [ERROR]")
        
        # Sleep between requests
        if i < NUM_REQUESTS:
            time.sleep(REQUEST_DELAY)
    
    print_separator()
    
    # Analyze results
    success_count = sum(1 for r in responses if r["status_code"] == 200)
    rate_limited_count = sum(1 for r in responses if r["status_code"] == 429)
    other_error_count = len(responses) - success_count - rate_limited_count
    
    print("Results Summary:")
    print(f"  Successful requests: {success_count}")
    print(f"  Rate limited requests: {rate_limited_count}")
    print(f"  Other errors: {other_error_count}")
    print_separator()
    
    # Display rate limit logs if running in Docker
    try:
        print("Rate Limiter Logs:")
        if os.path.exists("/app/logs/rate_limiter.log"):
            with open("/app/logs/rate_limiter.log", "r") as f:
                log_content = f.readlines()
                # Get the last 20 lines or all lines if fewer
                last_logs = log_content[-20:] if len(log_content) > 20 else log_content
                for line in last_logs:
                    print(f"  {line.strip()}")
        else:
            print("  Log file not accessible directly. If running outside Docker, check the logs using:")
            print("  docker compose exec api bash -c \"cat /app/logs/rate_limiter.log\"")
    except Exception as e:
        print(f"  Error accessing logs: {e}")
    
    print_separator()
    print("Test completed at:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

if __name__ == "__main__":
    main() 