# JWT Authentication Middleware

This directory contains middleware components for handling JWT authentication in the FastAPI application.

## JWT Verification Middleware

The `JWTVerificationMiddleware` is responsible for automatically verifying JWT tokens in incoming requests and providing authenticated user information to route handlers.

### Features

- **Automatic Token Verification**: Extracts and verifies JWT tokens from the `Authorization` header.
- **User Information in Request State**: Places decoded user information in `request.state.user` for easy access in route handlers.
- **Path Exclusions**: Configured to skip verification for certain paths like documentation, login routes, and health checks.
- **Centralized Authentication Logic**: Removes the need for explicit token verification in each route handler.

### How to Use

#### 1. In Protected Routes (Direct Access)

Access the authenticated user directly from the request state:

```python
@router.get("/protected")
async def protected_endpoint(request: Request):
    user = request.state.user
    return {"message": f"Hello, {user['username']}!"}
```

#### 2. With Dependency Helpers

Use the dependency helpers in `src.base.dependencies.jwt_dependencies`:

```python
@router.get("/protected")
async def protected_endpoint(
    current_user: dict = Depends(get_current_user_from_state),
    user_id: str = Depends(get_user_id_from_state),
    user_roles: list = Depends(get_user_roles_from_state)
):
    return {"message": f"Hello, user {user_id} with roles {user_roles}!"}
```

#### 3. Excluding Paths from Verification

The middleware is configured to exclude certain paths from JWT verification. To modify the excluded paths, update the `exclude_paths` parameter in the middleware registration in `src.base.system.register_middleware.py`.

## JWT Service

The JWT middleware uses the `JWTService` to handle token generation, verification, and decoding. The service is registered in the dependency injection container for use throughout the application.

### Example: Generating a Token

```python
@router.post("/login")
async def login(
    login_data: LoginData,
    jwt_service: JWTService = Depends(get_jwt_service)
):
    # Authenticate user and generate token
    token_data = {
        "sub": user_id,
        "username": username,
        "roles": roles
    }
    token = await jwt_service.create_token(token_data)
    return {"access_token": token, "token_type": "bearer"}
```

## Working with CORS and Other Middleware

The JWT middleware should be registered early in the middleware stack to ensure it runs after CORS middleware but before most other application-specific middleware. This ordering is important for proper handling of preflight requests and authentication flows.

## Testing Authentication

Example routes for testing the JWT authentication system are available in `src/domains/example/routes/auth_example.py`:

1. **Login**: Generate a token with a test user
2. **Verify Token**: Verify the validity of a token
3. **Protected Routes**: Access protected routes using different authentication approaches:
   - Direct dependency on `get_current_user`
   - JWT middleware with request state access
   - JWT middleware with state dependency helpers 