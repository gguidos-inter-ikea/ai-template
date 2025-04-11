# Logging System

This document describes the logging system in the FastAPI Microservice Boilerplate.

## Overview

The logging system in our application is designed to provide comprehensive visibility into the application's behavior, with the following features:

1. **Structured JSON Logging**: All logs are output in structured JSON format, making them easily parsable by log aggregation tools.
2. **Request Tracking**: Each request is assigned a unique ID that is included in all related logs.
3. **Comprehensive Request/Response Logging**: Detailed information is captured about each request and response.
4. **Security-Aware**: Sensitive information in headers and payloads is automatically redacted.
5. **Performance Metrics**: Response times are logged for each request.
6. **Error Tracing**: Detailed error information, including stack traces, is captured for debugging.

## Components

### 1. Request ID Middleware

The `RequestIDMiddleware` ensures that each request has a unique identifier that is:

- Generated when a request is received (if not provided in the `X-Request-ID` header)
- Stored in the request state for use by other middlewares and handlers
- Added to all log records via a ContextVar and filter
- Returned in the response headers

This allows for easy correlation of logs related to a single request, even in a distributed system.

### 2. Logging Middleware

The `LoggingMiddleware` captures comprehensive information about each request and response, including:

**Request Information:**
- HTTP method and URL
- Path and query parameters
- Client information (IP and port)
- Headers (with sensitive data redacted)
- Authentication type (without tokens)

**Response Information:**
- Status code and phrase
- Response time in milliseconds
- Headers (with sensitive data redacted)

**Error Information (when applicable):**
- Exception details and stack trace
- Request context for debugging

### 3. Structured JSON Formatter

The custom `StructuredJSONFormatter` formats log records as JSON objects, including:

- Standard fields (timestamp, level, message, etc.)
- Extra fields from the log record, such as request information
- Exception information when available

### 4. Log Files

The application logs to multiple files:

- `application.log`: All logs at INFO level and above
- `errors.log`: Error-level logs only
- `access.log`: HTTP access logs from the LoggingMiddleware
- `security.log`: Security-related events and unauthorized access attempts
- `rate_limiter.log`: Rate limit violations and related events

### 5. Security Event Logging

The logging system integrates with the security monitoring system to provide:

- **Real-time Event Processing**: Security events are logged and processed in real-time
- **Structured Event Data**: Security events are logged in a structured JSON format with:
  ```json
  {
    "event_type": "unauthorized_access",
    "client_ip": "192.168.1.100",
    "path": "/api/v1/users",
    "method": "POST",
    "reason": "invalid_token",
    "timestamp": "2024-03-15T19:52:08.123456"
  }
  ```
- **Historical Analysis**: Events are stored with timestamps for pattern analysis
- **Rate Limit Tracking**: Rate limit violations are logged with endpoint and client information
- **Error Correlation**: Security-related errors are correlated with request context

### 6. Log Rotation and Management

The logging system includes automatic log management features:

- **Size-based Rotation**: Logs are rotated when they reach 10MB
- **Backup Management**: Maintains 5 backup files per log type
- **Compression**: Rotated logs are automatically compressed
- **Cleanup**: Old log files are automatically removed based on retention policy

## Configuration

The logging system is configured in `src/base/config/logging_config.py`. Key configurations include:

- Log levels for different components
- Formatters for console and file output
- File locations for logs

## Usage

### Logging in Your Code

To log messages in your code:

```python
import logging

logger = logging.getLogger(__name__)

# Basic logging
logger.info("Simple log message")

# Structured logging with additional context
logger.info(
    "User action performed", 
    extra={
        "user_id": user.id,
        "action": "create_item",
        "item_id": item.id
    }
)

# Error logging
try:
    # Some operation
except Exception as e:
    logger.error(
        f"Failed to perform operation: {str(e)}", 
        exc_info=True,
        extra={"operation": "create_item"}
    )
```

### Accessing Request ID

To access the request ID in your route handlers:

```python
@router.get("/example")
async def example_route(request: Request):
    # Access the request ID
    request_id = request.state.request_id
    
    # Use it in logs or operations
    logger.info(f"Processing example route", extra={"custom_operation": "example"})
    
    return {"message": "Example", "request_id": request_id}
```

The request ID will automatically be included in all logs generated during request processing.

## Security Considerations

The logging system automatically redacts sensitive information:

- Authorization headers (only auth type is preserved)
- Cookies and other sensitive headers
- API keys

For additional sensitive data in your application, you should manually redact it before logging:

```python
# Instead of this
logger.info(f"User data: {user_data}")

# Do this
safe_user_data = {**user_data}
if "password" in safe_user_data:
    safe_user_data["password"] = "[REDACTED]"
logger.info(f"User data", extra={"user_data": safe_user_data})
```

## Log Analysis

The structured JSON logs can be easily analyzed using tools like:

- ELK Stack (Elasticsearch, Logstash, Kibana)
- Graylog
- Splunk
- Datadog

For local development, you can use `jq` to parse and filter logs:

```bash
# Show all error logs
cat logs/errors.log | jq

# Filter logs by request ID
cat logs/application.log | jq 'select(.request_id == "specific-request-id")'

# Find slow requests (>500ms)
cat logs/access.log | jq 'select(.response.duration_ms > 500)'
```

## Best Practices

1. **Use the Right Log Level**:
   - `DEBUG`: Detailed information for debugging
   - `INFO`: General operational information
   - `WARNING`: Something unexpected happened but the application can continue
   - `ERROR`: Something failed and needs attention
   - `CRITICAL`: The application cannot continue

2. **Include Context**: Always add relevant context to logs using the `extra` parameter.

3. **Don't Log Sensitive Information**: Be careful not to log PII, credentials, tokens, etc.

4. **Use Structured Logging**: Prefer structured logging over string concatenation.

5. **Log Request IDs in External Calls**: When making calls to other services, include the request ID in headers to maintain traceability.

## Excluded Paths

Certain paths are excluded from logging to reduce noise and improve performance:

```python
# Paths excluded from logging in LoggingMiddleware
EXCLUDED_PATHS = [
    "/internal/metrics",  # Prometheus metrics endpoint
    "/metrics",           # Backup path for metrics
    "/internal/health",   # Health check endpoint 
]
```

Additionally, the same paths are filtered from Uvicorn's access logs using a custom filter:

```python
class MetricsEndpointFilter(logging.Filter):
    """
    Filter to exclude requests to the metrics endpoint from Uvicorn access logs.
    """
    def __init__(self, excluded_paths=None):
        super().__init__()
        self.excluded_paths = excluded_paths or ["/internal/metrics", "/metrics", "/internal/health"]
    
    def filter(self, record):
        # Implementation details...
        # Returns False for metrics and health endpoints
        # Returns True for all other requests
```

This filtering is especially important for metrics endpoints that receive frequent scraping requests from Prometheus, which would otherwise flood the logs with repetitive entries.

### Customizing Excluded Paths

To modify the paths excluded from logging:

1. Update the `EXCLUDED_PATHS` list in `src/base/middlewares/logging.py`
2. Update the default paths in `MetricsEndpointFilter` in `src/base/config/logging_config.py` 