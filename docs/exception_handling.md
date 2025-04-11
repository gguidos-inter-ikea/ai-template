# Exception Handling

This document describes the exception handling system in the FastAPI Microservice Boilerplate. The system provides a robust way to handle errors, log them appropriately, and return consistent responses to clients.

## Overview

The exception handling system in our application is designed to:

1. Provide consistent error responses across the entire API
2. Track requests with unique IDs for better debugging and tracing
3. Format validation errors in a user-friendly way
4. Handle both framework-level and domain-specific exceptions
5. Adapt error details based on the environment (development vs. production)
6. Log errors with relevant contextual information
7. Categorize exceptions by domain and infrastructure

## Components

### 1. Exception Handlers

The main exception handlers are registered in `src/base/handlers/exception.py`. These handlers catch different types of exceptions and convert them to standardized JSON responses.

The following exception types are handled:

- `HTTPException` - FastAPI's standard HTTP exceptions
- `RequestValidationError` - FastAPI's request validation exceptions
- `ValidationError` - Pydantic's validation exceptions
- `StarletteHTTPException` - Starlette's HTTP exceptions
- `DomainException` - Custom domain-specific exceptions
- `InfrastructureException` - Custom infrastructure-specific exceptions
- `Exception` - Generic catch-all for unhandled exceptions

### 2. Request Tracking

Each request is assigned a unique ID using a UUID. This ID is:

- Stored in the request state
- Added to all error responses as the `X-Request-ID` header
- Included in log entries for easy correlation

This allows easy tracking of a request through the system, even across multiple services.

### 3. Exception Hierarchy

The application implements a hierarchical exception system:

```
Exception
│
├── DomainException
│   ├── [User Domain]
│   │   ├── UserNotFoundError
│   │   ├── DuplicateUserError
│   │   └── InvalidCredentialsError
│   │
│   └── [Other Domain]
│       ├── CustomDomainError1
│       └── CustomDomainError2
│
└── InfrastructureException
    ├── DatabaseConnectionError
    │   ├── MongoDBConnectionError
    │   └── RedisConnectionError
    │
    └── OtherInfrastructureError
```

### 4. Domain-Specific Exceptions

The `DomainException` class provides a way to raise business logic errors with custom status codes, error codes, and additional data:

```python
class DomainException(Exception):
    def __init__(
        self, 
        message: str, 
        status_code: int = 400, 
        error_code: str = None,
        data: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.data = data or {}
        self.domain = self.__class__.__module__.split('.')[-2]  # Extract domain from module path
        super().__init__(self.message)
```

Each domain should define its own exception classes that inherit from `DomainException`:

```python
# src/domains/user/exceptions.py
from src.base.handlers.exception import DomainException

class UserNotFoundError(DomainException):
    def __init__(self, user_id: str, message: str = None):
        super().__init__(
            message=message or f"User with ID {user_id} not found",
            status_code=404,
            error_code="USER_NOT_FOUND",
            data={"user_id": user_id}
        )

class DuplicateUserError(DomainException):
    def __init__(self, field: str, value: str, message: str = None):
        super().__init__(
            message=message or f"User with {field} '{value}' already exists",
            status_code=409,
            error_code="DUPLICATE_USER",
            data={"field": field, "value": value}
        )
```

### 5. Infrastructure Exceptions

The `InfrastructureException` class provides a way to handle infrastructure-related errors:

```python
class InfrastructureException(Exception):
    def __init__(
        self, 
        message: str, 
        status_code: int = 500, 
        data: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.data = data or {}
        super().__init__(self.message)
```

Specific infrastructure exceptions include:

```python
class DatabaseConnectionError(InfrastructureException):
    """Base exception for database connection issues."""
    def __init__(self, host: str, message: str = None, error_details: str = None):
        super().__init__(
            message=message or f"Failed to connect to database at {host}",
            status_code=503,  # Service Unavailable
            data={"host": host, "error_details": error_details}
        )

class MongoDBConnectionError(DatabaseConnectionError):
    """Exception raised when unable to connect to MongoDB."""
    pass

class RedisConnectionError(DatabaseConnectionError):
    """Exception raised when unable to connect to Redis."""
    pass
```

### 6. Validation Error Formatting

The system formats validation errors from Pydantic and FastAPI into a more user-friendly format:

```json
{
  "status": "error",
  "data": null,
  "message": "Validation error",
  "errors": [
    {
      "field": "username",
      "message": "field required",
      "type": "missing"
    }
  ]
}
```

### 7. Environment-Specific Behavior

In development environments, unhandled exceptions include more details to help with debugging. In production environments, these details are hidden to prevent leaking sensitive information.

## Usage

### Using Domain-Specific Exceptions

You should use domain-specific exceptions in your services and repositories to signal business logic errors:

```python
from src.domains.user.exceptions import UserNotFoundError, DuplicateUserError

async def get_user_by_id(user_id: str):
    user = await self.find_one({"_id": user_id})
    if not user:
        raise UserNotFoundError(user_id=user_id)
    return user

async def create_user(user_data: dict):
    # Check if user with same email exists
    existing_user = await self.find_one({"email": user_data["email"]})
    if existing_user:
        raise DuplicateUserError(field="email", value=user_data["email"])
    
    # Check if username is taken
    existing_user = await self.find_one({"username": user_data["username"]})
    if existing_user:
        raise DuplicateUserError(field="username", value=user_data["username"])
    
    # Create user
    return await self.insert_one(user_data)
```

### Handling Infrastructure Exceptions

The application automatically handles MongoDB and Redis connection issues by wrapping them in domain-specific exceptions:

```python
# In MongoDBClient
async def connect(self):
    """Connect to MongoDB."""
    try:
        self.client = AsyncIOMotorClient(self.db_uri)
        # Test the connection
        await self.client.admin.command('ping')
        self.db = self.client[self.db_name]
        return self.client
    except Exception as e:
        raise MongoDBConnectionError(
            host=self.db_uri,
            error_details=str(e),
            message=f"Failed to connect to MongoDB: {str(e)}"
        ) from e
```

The exception is then caught by the lifespan event handler during startup, properly logged, and returned as a clear error message.

### Error Response Format

All API error responses follow this format:

```json
{
  "status": "error",
  "data": {
    "domain": "user",          // For domain exceptions
    "error_code": "USER_NOT_FOUND",  // For domain exceptions
    "additional_info": {}      // Additional context data
  },
  "message": "User with ID 123 not found"
}
```

For validation errors, an additional `errors` field is included with detailed validation errors.

### Request Tracing

When reporting issues, the request ID from the `X-Request-ID` header should be included to help with debugging.

## Troubleshooting Database Connectivity Issues

The application includes utility scripts for troubleshooting database connection issues:

### Database Connection Test Script

```bash
# Test both MongoDB and Redis connections
python -m src.scripts.test_db_connection

# Test only MongoDB connection
python -m src.scripts.test_db_connection --mongodb

# Test only Redis connection
python -m src.scripts.test_db_connection --redis
```

### Docker Networking Fix Script

```bash
# Make the script executable
chmod +x src/scripts/fix_docker_networking.sh

# Run the script
./src/scripts/fix_docker_networking.sh
```

## Best Practices

1. **Use Domain-Specific Exceptions**: Define and use domain-specific exceptions instead of the generic `DomainException`.

2. **Include Context**: When raising exceptions, include useful context that helps understand the issue.

3. **Consistent Error Codes**: Use consistent error codes across the application with a proper naming convention:
   - `DOMAIN_ENTITY_ACTION_ERROR` (e.g., `USER_LOGIN_FAILED`, `PAYMENT_PROCESS_DECLINED`)

4. **Consistent Status Codes**: Use appropriate HTTP status codes consistently across the API.
   - 400: Bad Request (invalid input)
   - 401: Unauthorized (not authenticated)
   - 403: Forbidden (not authorized)
   - 404: Not Found
   - 409: Conflict (e.g., duplicate resource)
   - 422: Unprocessable Entity (validation errors)
   - 500: Internal Server Error
   - 503: Service Unavailable (database connection issues)

5. **Avoid Exposing Implementation Details**: Error messages should be user-friendly and not expose internal implementation details.

6. **Log Appropriately**: Make sure exceptions are logged with appropriate severity levels and context.

## Examples

### Domain-Specific Exception Example

```python
# src/domains/payment/exceptions.py
from src.base.handlers.exception import DomainException

class PaymentDeclinedError(DomainException):
    def __init__(self, payment_id: str, reason: str):
        super().__init__(
            message=f"Payment {payment_id} was declined: {reason}",
            status_code=400,
            error_code="PAYMENT_DECLINED",
            data={"payment_id": payment_id, "reason": reason}
        )

# Usage in service
from src.domains.payment.exceptions import PaymentDeclinedError

async def process_payment(payment_id: str, amount: float):
    # Process payment logic
    if payment_declined:
        raise PaymentDeclinedError(
            payment_id=payment_id,
            reason="Insufficient funds"
        )
```

### Infrastructure Exception Example

```python
# src/base/infrastructure/exceptions.py
from typing import Dict, Any, Optional

class InfrastructureException(Exception):
    def __init__(
        self, 
        message: str, 
        status_code: int = 500, 
        data: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.data = data or {}
        super().__init__(self.message)

# Usage
from src.base.infrastructure.exceptions import InfrastructureException

try:
    # Try to connect to external service
    response = await http_client.get("https://api.example.com/data")
except Exception as e:
    raise InfrastructureException(
        message="Failed to fetch data from external service",
        data={"service": "example_api", "error_details": str(e)}
    ) from e
```

## Testing Exceptions

When writing tests for code that may raise exceptions, you can assert that the correct exception is raised:

```python
import pytest
from src.domains.user.exceptions import UserNotFoundError

async def test_get_user_not_found():
    with pytest.raises(UserNotFoundError) as excinfo:
        await user_service.get_user_by_id("non_existent_id")
    
    assert excinfo.value.status_code == 404
    assert "not found" in excinfo.value.message
    assert excinfo.value.error_code == "USER_NOT_FOUND"
    assert excinfo.value.data["user_id"] == "non_existent_id"
``` 