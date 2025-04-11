from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from src.base.authentication.jwt import (
    create_access_token,
    verify_token,
    decode_token,
)
from src.base.config.config import settings
import logging

logger = logging.getLogger(__name__)

class JWTService:
    """Service for handling JWT tokens."""
    
    def __init__(self):
        """
        Initialize the JWT service with settings from the configuration.
        """
        self.secret_key = settings.security.jwt_secret_key
        self.algorithm = settings.security.jwt_algorithm
        self.expire_minutes = settings.security.jwt_expire_minutes
        logger.debug(f"JWT service initialized with algorithm: \
                     {self.algorithm}")

    async def create_token(
            self,
            data: Dict[str, Any],
            expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create a JWT token with the provided data.
        
        Args:
            data: The payload data to include in the token
            expires_delta: Optional expiration time override. If not provided, 
                          uses the default from settings.
        
        Returns:
            str: The generated JWT token
        """
        # Use provided expiration or default from settings
        expires = expires_delta or timedelta(minutes=self.expire_minutes)
        
        # Add expiration time to the data
        to_encode = data.copy()
        expiration_time = datetime.now() + expires
        to_encode.update({"exp": expiration_time})
        
        logger.debug(f"Creating JWT token for user ID: \
                     {data.get('sub', 'unknown')}")
        
        # Create and return the token
        return create_access_token(to_encode, self.secret_key, self.algorithm)

    async def verify_token(self, token: str) -> bool:
        """
        Verify if a JWT token is valid.
        
        Args:
            token: The JWT token to verify
            
        Returns:
            bool: True if token is valid, False otherwise
        """
        try:
            is_valid = verify_token(token, self.secret_key, self.algorithm)
            return is_valid
        except Exception as e:
            logger.warning(f"Token verification failed: {str(e)}")
            return False

    async def decode_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Decode a JWT token to get its payload.
        
        Args:
            token: The JWT token to decode
            
        Returns:
            Optional[Dict[str, Any]]: The decoded token payload or None
            if invalid
        """
        try:
            payload = decode_token(token, self.secret_key, self.algorithm)
            logger.debug(f"Token decoded successfully for user ID: \
                         {payload.get('sub', 'unknown')}")
            return payload
        except Exception as e:
            logger.warning(f"Token decoding failed: {str(e)}")
            return None
            
    async def get_user_id_from_token(self, token: str) -> Optional[str]:
        """
        Extract the user ID from a JWT token.
        
        Args:
            token: The JWT token
            
        Returns:
            Optional[str]: The user ID or None if not found or
            invalid token
        """
        payload = await self.decode_token(token)
        if payload and "sub" in payload:
            return payload["sub"]
        return None