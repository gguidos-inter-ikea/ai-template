"""
API Key Manager Module.

This module provides functionality for managing API keys, including generation, 
validation, and rotation. It uses Redis for storing and retrieving API keys
with appropriate expiration times.

The API Key Manager supports:
- Generating secure API keys with configurable expiration
- Validating API keys against Redis storage
- Determining when keys should be rotated based on age
"""
import secrets
import time
from typing import Optional
from dependency_injector.wiring import inject, Provide
from src.base.dependencies.di_container import Container
from src.base.repositories.redis_repository import RedisRepository

class ApiKeyManager:
    """
    Manages API keys with rotation capabilities.
    
    This class provides a complete API key lifecycle management system with:
    - Secure key generation using cryptographic functions
    - Redis-based storage with automatic expiration
    - Key validation for authentication
    - Key rotation suggestions based on key age
    """
    
    def __init__(self, redis_repository: RedisRepository):
        """
        Initialize the API Key Manager.
        
        Args:
            redis_repository: Redis repository for key storage and retrieval
        """
        self.redis = redis_repository
        self.key_prefix = "api_key:"
        self.rotation_period = 30 * 24 * 60 * 60  # 30 days in seconds
        
    async def generate_key(self, client_id: str) -> str:
        """
        Generate a new API key for a client.
        
        Creates a secure random API key, associates it with the client ID in Redis,
        and sets appropriate expiration times.
        
        Args:
            client_id: Unique identifier for the client/application
            
        Returns:
            str: The newly generated API key
        """
        api_key = secrets.token_urlsafe(32)
        expiry = int(time.time()) + self.rotation_period
        
        # Store the key with expiration
        await self.redis.set(
            f"{self.key_prefix}{api_key}",
            client_id,
            expiration=self.rotation_period
        )
        
        # Store the expiry timestamp for rotation checks
        await self.redis.set(
            f"{self.key_prefix}{client_id}:expiry",
            str(expiry),
            expiration=self.rotation_period + (7 * 24 * 60 * 60)  # Add 7 day grace period
        )
        
        return api_key
        
    async def validate_key(self, api_key: str) -> Optional[str]:
        """
        Validate an API key and return the client_id if valid.
        
        Args:
            api_key: The API key to validate
            
        Returns:
            str: The client ID associated with the key, or None if invalid
        """
        client_id = await self.redis.get(f"{self.key_prefix}{api_key}")
        return client_id
        
    async def should_rotate(self, client_id: str) -> bool:
        """
        Check if the client's API key should be rotated.
        
        Determines if the key is approaching its expiration date.
        This allows for proactive key rotation before expiry.
        
        Args:
            client_id: The client ID to check
            
        Returns:
            bool: True if the key should be rotated, False otherwise
        """
        expiry_str = await self.redis.get(f"{self.key_prefix}{client_id}:expiry")
        if not expiry_str:
            return True
            
        expiry = int(expiry_str)
        current_time = int(time.time())
        
        # Suggest rotation when we're within 20% of expiry time
        rotation_window = self.rotation_period * 0.2
        return (expiry - current_time) < rotation_window
        
    async def invalidate_key(self, api_key: str) -> bool:
        """
        Invalidate an API key immediately.
        
        This can be used when a key is compromised or no longer needed.
        
        Args:
            api_key: The API key to invalidate
            
        Returns:
            bool: True if the key was invalidated, False if it didn't exist
        """
        return await self.redis.delete(f"{self.key_prefix}{api_key}")