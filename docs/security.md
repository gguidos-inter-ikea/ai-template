# Security Features

This document outlines the security features available in the application and how to implement them effectively.

## Table of Contents

- [JWT Authentication](#jwt-authentication)
- [API Key Management](#api-key-management)
- [IP Filtering](#ip-filtering)
- [Session Tracking](#session-tracking)
- [Security Headers](#security-headers)
- [Input Validation](#input-validation)
- [Rate Limiting](#rate-limiting)
- [Security Monitoring](#security-monitoring)

## JWT Authentication

The application uses JWT (JSON Web Tokens) for stateless authentication.

### Setup and Configuration

JWT authentication is configured in `src/base/authentication/jwt.py`. The following settings can be configured in your `.env` file:

```
JWT_SECRET_KEY=your-very-secure-secret-key-keep-it-safe
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=30
```

> **IMPORTANT**: Never commit real secret keys to version control. Always use environment variables or secure secrets management.

### Usage in Routes

To implement JWT authentication in your routes:

```python
from fastapi import Depends
from src.base.dependencies.auth import get_auth_user, get_admin_user, requires_role

# Basic authentication - requires valid token
@router.get("/me")
async def read_users_me(current_user = Depends(get_auth_user)):
    return current_user

# Admin-only endpoint
@router.get("/admin/stats")
async def admin_stats(current_user = Depends(get_admin_user)):
    return {"message": "Admin only stats", "user": current_user}

# Role-based access control
@router.get("/finance")
async def finance_data(current_user = Depends(requires_role("finance"))):
    return {"message": "Finance data", "user": current_user}
```

### Token Generation

Create tokens at login or registration:

```python
from src.base.authentication.jwt import create_access_token

@router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # Validate user credentials (implementation specific)
    user = authenticate_user(form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Create token with user ID as subject
    access_token = create_access_token(data={"sub": user["id"]})
    
    return {"access_token": access_token, "token_type": "bearer"}
```

## API Key Management

The application includes an API key management system with automatic rotation capabilities.

### Features

- Secure key generation using cryptographic functions
- Automatic key rotation based on configurable timeframes
- Key validation with client identification

### Configuration

API keys are managed by the `ApiKeyManager` class in `src/base/security/api_key_manager.py`. The default configuration:

- Rotation period: 30 days
- Rotation suggestion: When within 20% of expiration (approximately 6 days)
- Key format: URL-safe Base64 encoded token (32 bytes)

### Implementation Example

```python
from dependency_injector.wiring import Provide, inject
from src.base.dependencies.di_container import Container
from src.base.security.api_key_manager import ApiKeyManager

class ApiKeyService:
    @inject
    def __init__(self, api_key_manager: ApiKeyManager = Provide[Container.api_key_manager]):
        self.api_key_manager = api_key_manager
        
    async def create_key_for_client(self, client_id: str):
        return await self.api_key_manager.generate_key(client_id)
        
    async def validate_client_key(self, api_key: str):
        client_id = await self.api_key_manager.validate_key(api_key)
        if not client_id:
            raise ValueError("Invalid API key")
        return client_id
        
    async def check_rotation_needed(self, client_id: str):
        return await self.api_key_manager.should_rotate(client_id)
```

## IP Filtering

The application implements IP-based access control for protected paths.

### Configuration

IP filtering is implemented via the `IPFilterMiddleware` in `src/base/middlewares/ip_filter.py`.

Protected paths include:
- `/admin/*` - Admin endpoints
- `/internal/*` - Internal endpoints 

Public paths (exempt from IP filtering) include:
- `/internal/metrics` - Prometheus metrics endpoint
- `/metrics` - Alternative metrics endpoint
- `/internal/health` - Health check endpoint

Configure allowed IPs in your `.env` file:

```
ALLOWED_ADMIN_IPS=127.0.0.1,10.0.0.5
```

### Customization

You can customize the protected and public paths when registering the middleware:

```python
# In src/base/system/register_middleware.py
app.add_middleware(
    IPFilterMiddleware,
    allowed_ips=settings.allowed_admin_ips,
    protected_paths=["/admin", "/internal", "/sensitive"],
    public_paths=["/internal/metrics", "/internal/health", "/public"]
)
```

## Session Tracking

The application includes a Redis-based session tracking system that tracks requests and responses.

### Functionality

- Tracks all user sessions based on IP address and (when available) user ID
- Records request/response pairs with performance metrics
- Maintains a history of recent requests (limited to 100 entries per session)
- Support for examining user journey and detecting anomalies

### Configuration

Session tracking is implemented in `src/base/services/session_tracker.py`.

- Sessions expire after 2 hours by default
- Redis keys use the pattern: `{prefix}:session:{session_id}:*`

### Integration with Logging Middleware

The session tracking is automatically integrated with the logging middleware to track all requests:

```python
# Already integrated in src/base/middlewares/logging.py
client_ip = request.client.host if request.client else None
user_id = getattr(request.state, "user", {}).get("id", None)
            
session_id = await SessionTracker.record_request(
    client_ip=client_ip,
    user_id=user_id,
    request_path=request.url.path,
    request_method=request.method,
    request_id=request_id
)
```

### Accessing Session Data

To retrieve session data for analysis:

```python
from src.base.services.session_tracker import SessionTracker

@router.get("/debug/sessions/{session_id}")
async def get_session(session_id: str):
    session_data = await SessionTracker.get_session_history(session_id)
    if not session_data:
        raise HTTPException(status_code=404, detail="Session not found")
    return session_data
```

## Security Headers

The application automatically adds security headers to all responses via the `SecurityHeadersMiddleware`. These headers implement defense in depth by protecting against various web security vulnerabilities.

### Headers Applied

- **Strict-Transport-Security (HSTS)**
  - Value: `max-age=63072000; includeSubDomains; preload`
  - Purpose: Forces HTTPS connections for 2 years
  - Applies to all subdomains
  - Eligible for browser preload lists

- **Content-Security-Policy (CSP)**
  ```
  default-src 'self';
  script-src 'self' 'unsafe-inline' cdn.jsdelivr.net blob:;
  style-src 'self' 'unsafe-inline' cdn.jsdelivr.net;
  img-src 'self' data: fastapi.tiangolo.com;
  font-src 'self' data: cdn.jsdelivr.net;
  connect-src 'self';
  worker-src 'self' blob:;
  frame-ancestors 'none';
  form-action 'self';
  ```
  - Controls which resources can be loaded and from where
  - Allows necessary resources for Swagger UI and ReDoc
  - Allows Web Workers from blob URLs for ReDoc functionality
  - Prevents XSS and other injection attacks

- **X-Content-Type-Options**
  - Value: `nosniff`
  - Prevents browsers from MIME type sniffing
  - Reduces exposure to drive-by download attacks

- **X-Frame-Options**
  - Value: `DENY`
  - Prevents site from being embedded in frames
  - Protects against clickjacking attacks

- **X-XSS-Protection**
  - Value: `1; mode=block`
  - Enables browser's built-in XSS filter
  - Blocks page rather than sanitizing when XSS is detected

- **Referrer-Policy**
  - Value: `no-referrer`
  - Controls how much referrer information is included
  - Enhances privacy by not sending referrer information

- **Permissions-Policy**
  ```
  accelerometer=(),
  autoplay=(),
  camera=(),
  geolocation=(),
  gyroscope=(),
  magnetometer=(),
  microphone=(),
  payment=(),
  usb=()
  ```
  - Restricts access to sensitive browser features
  - Enhances privacy and security
  - Prevents unauthorized access to device capabilities

### Implementation

The security headers are implemented in `src/base/middlewares/security_headers.py`. The middleware:
1. Intercepts all responses
2. Adds the security headers
3. Ensures consistent security policy across the application

### Customization

You can customize the security headers by modifying the `SecurityHeadersMiddleware`:

```python
# In src/base/middlewares/security_headers.py
async def dispatch(self, request: Request, call_next):
    response = await call_next(request)
    
    # Customize headers as needed
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' your-trusted-domain.com; "
        # ... other directives ...
    )
    
    return response
```

### Best Practices

1. **Review Regularly**: Security headers should be reviewed and updated regularly
2. **Test Changes**: Use tools like [Security Headers](https://securityheaders.com) to validate changes
3. **Monitor Effects**: Watch for unintended side effects when modifying headers
4. **Document Changes**: Keep this documentation updated when modifying security policies

### Related Resources

- [OWASP Secure Headers Project](https://owasp.org/www-project-secure-headers/)
- [MDN Web Security](https://developer.mozilla.org/en-US/docs/Web/Security)
- [Content Security Policy Reference](https://content-security-policy.com/)

## Input Validation

The application uses Pydantic models for input validation.

### Best Practices

1. **Create validation models**: Use Pydantic models for all input data
2. **Custom validators**: Add custom validators for business logic validation
3. **Field constraints**: Use field constraints for basic validation

```python
from pydantic import BaseModel, Field, validator
from typing import Optional

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., regex=r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
    password: str = Field(..., min_length=8)
    
    @validator('username')
    def username_alphanumeric(cls, v):
        if not v.isalnum():
            raise ValueError('must be alphanumeric')
        return v
```

## Rate Limiting

The application includes rate limiting to prevent abuse. See [Rate Limiting](rate_limiting.md) for details.

## Security Monitoring

The application includes a comprehensive security monitoring system that provides real-time monitoring, logging, and alerting for security events and system errors.

### Features

- **Real-time Event Processing**: Monitors and analyzes security events in real-time
- **Historical Analysis**: Maintains event history for pattern detection and analysis
- **Attack Pattern Detection**: Analyzes patterns of unauthorized access and rate limit violations
- **Multi-Channel Alerts**: Rich HTML and plain text email alerts with comprehensive event details
- **Configurable Thresholds**: Customizable thresholds for different types of security events
- **Cooldown Periods**: Prevents alert fatigue with configurable cooldown periods
- **Automatic Log Rotation**: Manages log files with size limits and backup counts

### Configuration

Configure the security monitor through environment variables or command-line arguments:

```ini
# Email Alert Settings
EMAIL_ALERTS_ENABLED=true
EMAIL_SMTP_SERVER=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_SENDER=your.email@gmail.com
EMAIL_PASSWORD=your_app_password
EMAIL_RECIPIENTS=["security@yourcompany.com"]
EMAIL_USE_TLS=true

# Monitor Settings
SECURITY_LOG_PATH=/app/logs/security.log
RATE_LIMIT_LOG_PATH=/app/logs/rate_limiter.log
ERROR_LOG_PATH=/app/logs/errors.log
```

### Command-Line Usage

Start the security monitor with custom settings:

```bash
python -m src.base.scripts.security_monitor \
    --security-log /path/to/security.log \
    --rate-limit-log /path/to/rate_limiter.log \
    --error-log /path/to/errors.log \
    --enabled-logs security,rate_limit,error \
    --unauthorized-threshold 3 \
    --rate-limit-threshold 5 \
    --cooldown 5 \
    --time-window 60
```

### Alert Information

Security alerts include comprehensive information:

- **Alert Summary**:
  - Event type and description
  - Latest impact (number of attempts and unique IPs)
  - Historical impact over the time window
  - Time and date of the alert

- **Security Analysis**:
  - Total rate limit violations
  - Most targeted endpoints
  - Attack pattern classification
  - IP-based statistics

- **Detailed Information**:
  - Client IP addresses
  - Request paths and methods
  - User agents
  - Attempt counts
  - Historical statistics

### Email Alert Format

Alerts are sent in both HTML and plain text formats:

- **HTML Format**:
  - Styled, responsive layout
  - Color-coded sections for different types of information
  - Tabulated data for easy reading
  - Collapsible JSON details for additional information

- **Plain Text Format**:
  - Structured sections with clear headings
  - Formatted lists and tables
  - Complete event details in a readable format

### Integration

The security monitor integrates with:
- FastAPI application logs
- Rate limiting middleware
- Authentication middleware
- Session tracking system
- Prometheus metrics (optional)

### Best Practices

1. **Configure Thresholds**: Set appropriate thresholds based on your application's traffic patterns
2. **Enable Multiple Log Types**: Monitor security, rate limit, and error logs for comprehensive coverage
3. **Set Appropriate Time Windows**: Balance between detecting patterns and maintaining performance
4. **Use TLS for Email**: Always use TLS when configuring email alerts
5. **Regular Review**: Periodically review alert patterns to adjust thresholds and cooldown periods

For detailed implementation information, see the [Security Monitor Documentation](../src/base/scripts/SECURITY_MONITOR.md).

## Related Documentation

- [Exception Handling](exception_handling.md)
- [Rate Limiting](rate_limiting.md)
- [Logging](logging.md)
- [Monitoring](monitoring.md) 