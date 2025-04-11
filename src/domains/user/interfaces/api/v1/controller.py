from fastapi import APIRouter, Depends, HTTPException, status
from src.domains.user.dependencies.get_user_service import get_user_service
from src.domains.user.services.user_service import UserService
from src.domains.user.exceptions import InvalidCredentialsError
from src.base.services.jwt_service import JWTService
from src.base.dependencies.jwt_dependencies import get_jwt_service
from src.base.dependencies.rate_limiter_dependencies import (
    get_standard_write_rate_limiter,
    get_standard_read_rate_limiter
)
from pydantic import BaseModel
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

class UserCreateRequest(BaseModel):
    name: str
    email: str
    password: str

class UserLoginRequest(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    """Token response model."""
    access_token: str
    token_type: str = "bearer"

@router.post("/api/v1/user/registration")
async def create_user(
    request: UserCreateRequest,
    user_service: UserService = Depends(get_user_service),
    # Use the rate limiter via dependency injection
    _=Depends(get_standard_write_rate_limiter())
):
    """
    Create a new user.
    
    Rate limited to 5 requests per minute per client.
    """
    try:
        # Convert Pydantic model to dictionary
        user_data = request.model_dump()
        return await user_service.create_user(user_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/v1/users")
async def get_users(
    user_service: UserService = Depends(get_user_service),
    # Use the rate limiter via dependency injection
    _=Depends(get_standard_read_rate_limiter())
):
    """
    Get all users.
    
    Rate limited to 100 requests per minute per client.
    """
    return await user_service.get_users()

@router.post("/api/v1/users/login", response_model=Token)
async def login(
    request: UserLoginRequest,
    user_service: UserService = Depends(get_user_service),
    jwt_service: JWTService = Depends(get_jwt_service),
    # Use the rate limiter via dependency injection
    _=Depends(get_standard_write_rate_limiter())
):
    """
    Login a user.
    
    Rate limited to 5 requests per minute per client.
    """
    try:
        logger.info(f"Login request received for email: {request.email}")

        authenticated_user = await user_service.authenticate_user(request.email, request.password)
        logger.info(f"{authenticated_user}")
        token_data = {
            "sub": authenticated_user['_id'],  # Correct: using dictionary key access
            "name": authenticated_user['name'],
            "email": authenticated_user['email'],
            "roles": ["user"]
        }
    
        # Generate token using JWT service
        token = await jwt_service.create_token(token_data)
        
        return {"access_token": token, "token_type": "bearer"}
    except InvalidCredentialsError:
        # Return a 401 Unauthorized for invalid credentials
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        # Log the actual error but return a generic message to the user
        logger.error(f"Login error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An error occurred during authentication"
        )