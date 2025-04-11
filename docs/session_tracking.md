# Session Tracking

This document explains the session tracking system implemented in the API for monitoring and analyzing user activity.

## Overview

The session tracking system provides a way to monitor and analyze API usage patterns by tracking all requests and responses for each client. This enables:

- **User Journey Analysis**: Track how users navigate through your API
- **Performance Monitoring**: Identify slow endpoints for specific clients
- **Security Analysis**: Detect suspicious activity patterns
- **Debugging**: Trace issues reported by specific clients
- **Usage Analytics**: Understand how clients are using your API

## Architecture

The session tracking system consists of several components:

1. **SessionTracker Service**: Core service that manages session data
2. **Redis Repository**: Persistence layer for session data
3. **Logging Middleware Integration**: Captures requests/responses automatically

### Data Flow

1. A request arrives at the API
2. The logging middleware intercepts the request
3. The middleware calls `SessionTracker.record_request()`
4. The session tracker creates or retrieves a session for the client
5. After the request is processed, the middleware calls `SessionTracker.record_response()`
6. Both request and response data are stored in Redis with appropriate expiration

## Session Identification

Sessions are identified in two ways:

1. **By User ID**: When the user is authenticated
2. **By IP Address**: When the user is not authenticated

This allows tracking both authenticated and anonymous users, with authenticated users having consistent tracking across IP changes.

## Data Structure

Session data is stored in Redis using the following key structure:

- `{prefix}:session:{session_id}:info` - Session metadata (client IP, user ID, creation time)
- `{prefix}:session:{session_id}:requests` - List of request records
- `{prefix}:session:{session_id}:responses` - List of response records
- `{prefix}:session:user:{user_id}` - Mapping from user ID to session ID
- `{prefix}:session:ip:{client_ip}` - Mapping from IP address to session ID

### Request Record

```json
{
  "timestamp": 1647123456,
  "path": "/api/users",
  "method": "GET",
  "request_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### Response Record

```json
{
  "timestamp": 1647123456,
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "status_code": 200,
  "duration_ms": 45.23
}
```

## Configuration

The session tracking system is configured in `src/base/services/session_tracker.py`:

```python
# Prefix for Redis keys to avoid collisions
KEY_PREFIX = f"{settings.redis_prefix}:session:"

# Default session expiration (2 hours)
DEFAULT_EXPIRY = 7200
```

You can adjust these settings to match your requirements:

- Increase `DEFAULT_EXPIRY` for longer-lived sessions
- Modify `KEY_PREFIX` to avoid key collisions in shared Redis instances

## Usage Examples

### Getting Session History

To retrieve and analyze session history:

```python
from src.base.services.session_tracker import SessionTracker

async def get_user_session(user_id: str):
    # First get the session ID for the user
    session_id = await redis_repository.get(f"{SessionTracker.KEY_PREFIX}user:{user_id}")
    
    if not session_id:
        return None
        
    # Get the full session history
    session_data = await SessionTracker.get_session_history(session_id)
    return session_data
```

### Creating an Analytics Endpoint

You can create an admin endpoint to analyze session data:

```python
from fastapi import APIRouter, Depends, HTTPException
from src.base.services.session_tracker import SessionTracker
from src.base.dependencies.auth import get_admin_user

router = APIRouter()

@router.get("/admin/analytics/sessions/{session_id}")
async def get_session_analytics(
    session_id: str,
    current_user = Depends(get_admin_user)
):
    """Get analytics for a specific session"""
    session_data = await SessionTracker.get_session_history(session_id)
    
    if not session_data:
        raise HTTPException(status_code=404, detail="Session not found")
        
    # Basic analytics
    request_count = len(session_data["requests"])
    response_times = [r["duration_ms"] for r in session_data["responses"]]
    avg_response_time = sum(response_times) / len(response_times) if response_times else 0
    error_count = sum(1 for r in session_data["responses"] if r["status_code"] >= 400)
    
    return {
        "session_id": session_id,
        "user_id": session_data["info"]["user_id"],
        "client_ip": session_data["info"]["client_ip"],
        "created_at": session_data["info"]["created_at"],
        "analytics": {
            "request_count": request_count,
            "avg_response_time": avg_response_time,
            "error_count": error_count,
            "error_rate": error_count / request_count if request_count else 0
        }
    }
```

## Security Considerations

The session tracking system stores potentially sensitive information:

1. **IP Addresses**: Subject to privacy regulations like GDPR
2. **User IDs**: Can be used to identify individuals
3. **Usage Patterns**: May reveal sensitive information

### Recommendations

- Set appropriate TTL values to avoid storing data longer than necessary
- Implement access controls for any endpoints that expose session data
- Consider anonymizing IP addresses for privacy compliance
- Be cautious about logging sensitive request paths (e.g., `/login`, `/reset-password`)

## Performance Impact

The session tracking system adds some overhead to request processing:

1. **Redis Operations**: Multiple Redis operations per request
2. **JSON Serialization**: Request/response data must be serialized
3. **Storage Growth**: Each request/response pair consumes storage

### Optimizations

- Use the `EXCLUDED_PATHS` in the `LoggingMiddleware` to skip tracking for high-volume endpoints
- Adjust `ltrim` limits to control storage growth
- Consider implementing sampling for high-traffic applications

## Related Documentation

- [Redis Repository Pattern](repository_pattern.md)
- [Logging System](logging.md)
- [Security Features](security.md) 