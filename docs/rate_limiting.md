# Rate Limiting in the API

This document explains how to use the rate limiting functionality in the API.

## Overview

Rate limiting is a technique used to control the amount of incoming and outgoing traffic to or from a network, application, or service. In our API, we use Redis-based rate limiting to:

1. Prevent abuse of the API
2. Ensure fair usage among clients
3. Protect the API from being overwhelmed by too many requests

## Available Rate Limiters

The API provides several pre-configured rate limiters:

| Rate Limiter | Limit | Description |
|--------------|-------|-------------|
| `default_rate_limiter` | 100 requests per minute | Default rate limiting for most endpoints |
| `strict_rate_limiter` | 20 requests per minute | Stricter rate limiting for sensitive endpoints |
| `very_strict_rate_limiter` | 5 requests per minute | Very strict rate limiting for critical endpoints |
| `ip_rate_limiter` | 100 requests per minute per IP | Rate limiting based on client IP address |
| `api_key_rate_limiter` | 200 requests per minute per API key | Rate limiting based on API key |
| `combined_rate_limiter` | Both IP and API key limits | Combined rate limiting using both IP and API key |

## How to Apply Rate Limiting

### Method 1: Using Dependencies

You can apply rate limiting to an endpoint by adding a rate limiter as a dependency:

```python
from fastapi import APIRouter, Depends, Request
from src.base.system.rate_limiter import default_rate_limiter

router = APIRouter()

@router.get("/my-endpoint")
async def my_endpoint(
    request: Request,
    _=Depends(default_rate_limiter)
):
    return {"message": "This endpoint is rate limited"}
```

### Method 2: Using Multiple Rate Limiters

You can apply multiple rate limiters to a single endpoint:

```python
from fastapi import APIRouter, Depends, Request
from src.base.system.rate_limiter import ip_rate_limiter, api_key_rate_limiter

router = APIRouter()

@router.get("/my-endpoint")
async def my_endpoint(
    request: Request,
    _=Depends(ip_rate_limiter),
    __=Depends(api_key_rate_limiter)
):
    return {"message": "This endpoint has multiple rate limiters"}
```

### Method 3: Using the Combined Rate Limiter

For more complex rate limiting scenarios, you can use the `CombinedRateLimiter` class:

```python
from fastapi import APIRouter, Depends, Request
from src.base.system.rate_limiter import combined_rate_limiter

router = APIRouter()

@router.get("/my-endpoint")
async def my_endpoint(
    request: Request,
    _=Depends(combined_rate_limiter)
):
    return {"message": "This endpoint has combined rate limiting"}
```

You can also create your own combined rate limiter:

```python
from fastapi import APIRouter, Depends, Request
from src.base.system.rate_limiter import CombinedRateLimiter, ip_rate_limiter, create_rate_limiter

# Create a custom rate limiter
custom_limiter = create_rate_limiter(times=50, seconds=60)

# Combine it with the IP rate limiter
my_combined_limiter = CombinedRateLimiter([
    ip_rate_limiter,
    custom_limiter
])

router = APIRouter()

@router.get("/my-endpoint")
async def my_endpoint(
    request: Request,
    _=Depends(my_combined_limiter)
):
    return {"message": "This endpoint has custom combined rate limiting"}
```

### Method 4: Using the Decorator

You can also use the `rate_limited` decorator to apply rate limiting:

```python
from fastapi import APIRouter, Request
from src.base.system.rate_limiter import rate_limited

router = APIRouter()

@router.get("/my-endpoint")
@rate_limited(times=10, seconds=60)  # 10 requests per minute
async def my_endpoint(request: Request):
    return {"message": "This endpoint is rate limited"}
```

Or use a pre-configured rate limiter:

```python
from fastapi import APIRouter, Request
from src.base.system.rate_limiter import rate_limited, strict_rate_limiter

router = APIRouter()

@router.get("/my-endpoint")
@rate_limited(limiter=strict_rate_limiter)
async def my_endpoint(request: Request):
    return {"message": "This endpoint is rate limited"}
```

## Creating Custom Rate Limiters

You can create custom rate limiters with specific limits:

```python
from src.base.system.rate_limiter import create_rate_limiter

# Create a rate limiter that allows 50 requests per hour
my_custom_limiter = create_rate_limiter(times=50, seconds=3600)
```

You can also create a rate limiter with a custom identifier function:

```python
from fastapi import Request
from src.base.system.rate_limiter import create_rate_limiter

def user_id_identifier(request: Request) -> str:
    user_id = request.headers.get("User-ID", "anonymous")
    return f"user:{user_id}"

# Create a rate limiter that limits by user ID
user_rate_limiter = create_rate_limiter(
    times=100, 
    seconds=60, 
    identifier=user_id_identifier
)
```

## Rate Limiting Response

When a client exceeds the rate limit, the API will respond with a `429 Too Many Requests` status code and a JSON response:

```json
{
  "detail": "Rate limit exceeded: 100 requests per 60 seconds"
}
```

## Example Endpoints

The API includes example endpoints that demonstrate different rate limiting strategies:

- `/internal/rate-limit-examples/default-limited` - Default rate limiting
- `/internal/rate-limit-examples/strict-limited` - Strict rate limiting
- `/internal/rate-limit-examples/very-strict-limited` - Very strict rate limiting
- `/internal/rate-limit-examples/ip-limited` - IP-based rate limiting
- `/internal/rate-limit-examples/api-key-limited` - API key-based rate limiting
- `/internal/rate-limit-examples/combined-limited` - Combined rate limiting with multiple dependencies
- `/internal/rate-limit-examples/combined-chain` - Combined rate limiting using CombinedRateLimiter

You can use these endpoints to test and understand how rate limiting works in the API. 

## Rate Limit Logging

The API includes a specialized logging system for rate limit events, which provides visibility into rate limiting behavior.

### Log Configuration

Rate limit events are logged to a dedicated log file:

- **File Path**: `/app/logs/rate_limiter.log`
- **Format**: Text logs with timestamp, severity level, and detailed message
- **Events Logged**: 
  - Rate limiter initialization
  - Rate limit approaching (warning)
  - Rate limit exceeded (error)

### Example Log Entries

Example of a rate limit exceeded log entry:

```
1695928472 [WARNING] Rate limit exceeded for endpoint /api/v1/users | Client: ip:192.168.65.1 | Limit: 5 requests per 60 seconds
```

### Monitoring Rate Limit Events

To monitor rate limit events:

```bash
# View the rate limiter log
docker compose exec api cat /app/logs/rate_limiter.log

# Watch for new rate limit events in real-time
docker compose exec api tail -f /app/logs/rate_limiter.log
```

Rate limit logs can be used to:
1. Monitor abuse patterns
2. Identify endpoints that are frequently hitting limits
3. Adjust rate limit settings based on real-world usage
4. Troubleshoot client issues

## Testing Rate Limiting

The API includes comprehensive tests for rate limiting functionality. To run these tests:

```bash
# Reset Redis to clear any existing rate limit counters
docker compose exec redis redis-cli FLUSHDB

# Run the rate limiter integration tests
docker compose exec api pytest tests/integration/test_user_api.py -v
```

### Testing Rate Limit Logging

The integration tests include a specific test for rate limit logging that:

1. Clears any existing rate limit counters
2. Makes multiple requests to trigger a rate limit
3. Verifies that rate limit events are properly logged

For more details on testing, see the [Tests README](/tests/README.md). 