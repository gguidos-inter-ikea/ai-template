"""
JWT Authentication module.

This module provides JWT (JSON Web Token) based authentication for the API.
It includes functions for token creation and validation, enabling stateless 
authentication for API endpoints.

Usage:
- Use `create_access_token()` to generate tokens at login/registration
- Use `decode_token()` to extract data from a token
- Use `verify_token()` to validate a token without extracting data
- Use `get_current_user()` as a dependency in protected routes
"""
from jose import JWTError, jwt, ExpiredSignatureError
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from src.base.config.config import settings
import logging

logger = logging.getLogger(__name__)

# Configuration from settings
SECRET_KEY = settings.security.jwt_secret_key
ALGORITHM = settings.security.jwt_algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.security.jwt_expire_minutes

# Create OAuth2 password bearer scheme for token extraction
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_access_token(
        data: dict,
        secret_key: str = SECRET_KEY,
        algorithm: str = ALGORITHM,
        expires_delta: timedelta = None
):
    """
    Create a new JWT access token.
    
    Args:
        data (dict): The payload data to encode in the token
        secret_key (str): The secret key to use for signing the token
        algorithm (str): The algorithm to use for signing the token
        expires_delta (timedelta, optional): Custom expiration time,
            defaults to ACCESS_TOKEN_EXPIRE_MINUTES from settings
            
    Returns:
        str: The encoded JWT token string
    """
    to_encode = data.copy()
    expire = \
        datetime.now() +\
        (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, secret_key, algorithm=algorithm)

def decode_token(
        token: str,
        secret_key: str = SECRET_KEY,
        algorithm: str = ALGORITHM
):
    """
    Decode a JWT token and return its payload.
    
    Args:
        token (str): The JWT token to decode
        secret_key (str): The secret key used to sign the token
        algorithm (str): The algorithm used to sign the token
        
    Returns:
        dict: The decoded token payload
        
    Raises:
        JWTError: If the token is invalid or expired
    """
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        return payload
    except ExpiredSignatureError:
        logger.warning("Token has expired")
        raise
    except JWTError as e:
        logger.warning(f"Invalid token: {str(e)}")
        raise

def verify_token(
        token: str,
        secret_key: str = SECRET_KEY,
        algorithm: str = ALGORITHM
):
    """
    Verify that a JWT token is valid without decoding its contents.
    
    Args:
        token (str): The JWT token to verify
        secret_key (str): The secret key used to sign the token
        algorithm (str): The algorithm used to sign the token
        
    Returns:
        bool: True if the token is valid, False otherwise
    """
    try:
        # Attempt to decode the token - if it succeeds, the token is valid
        jwt.decode(token, secret_key, algorithms=[algorithm])
        return True
    except:
        return False

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Validate JWT token and return the authenticated user.
    
    This function can be used as a FastAPI dependency to protect routes.
    
    Args:
        token (str): The JWT token extracted from the Authorization header
            (automatically handled by the oauth2_scheme dependency)
            
    Returns:
        dict: User information extracted from the token
        
    Raises:
        HTTPException: With 401 status code if token is invalid
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode and validate the token
        payload = decode_token(token)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    # Get user from database here
    # user = await get_user(user_id)
    # if user is None:
    #     raise credentials_exception
    # return user
    
    # For now, just return basic user info from token
    return {"id": user_id}
