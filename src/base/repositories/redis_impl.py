"""
Redis Repository Implementation.

This module provides a concrete implementation of the RedisRepository interface
using aioredis for asynchronous Redis operations.
"""
from typing import List, Optional, AsyncIterator
import aioredis
from src.base.repositories.redis_repository import RedisRepository

class RedisRepositoryImpl(RedisRepository):
    """
    Implementation of the RedisRepository interface.
    
    This class provides concrete implementations of all methods defined in the
    RedisRepository interface, using aioredis for actual Redis operations.
    """
    
    def __init__(self, redis_client: aioredis.Redis):
        """
        Initialize the Redis repository.
        
        Args:
            redis_client: An initialized aioredis Redis client
        """
        self.redis = redis_client
    
    async def get(self, key: str) -> Optional[str]:
        """
        Get a value from Redis by key.
        
        Args:
            key: The Redis key to retrieve
            
        Returns:
            The value if found, None otherwise
        """
        value = await self.redis.get(key)
        return value
    
    async def set(self, key: str, value: str, expiration: Optional[int] = None) -> bool:
        """
        Set a key-value pair in Redis.
        
        Args:
            key: The Redis key
            value: The value to store
            expiration: Optional expiration time in seconds
            
        Returns:
            True if successful, False otherwise
        """
        if expiration:
            return await self.redis.set(key, value, ex=expiration)
        return await self.redis.set(key, value)
    
    async def subscribe_channel(self, channel: str) -> AsyncIterator[str]:
        pubsub = self.redis.pubsub()
        await pubsub.subscribe(channel)

        try:
            async for message in pubsub.listen():
                if message["type"] == "message":
                    yield message["data"].decode()
        finally:
            await pubsub.unsubscribe(channel)
            await pubsub.close()
    
    async def lpush(self, key: str, value: str) -> int:
        """
        Push a value to the left of a Redis list.
        
        Args:
            key: The Redis list key
            value: The value to push
            
        Returns:
            The new length of the list
        """
        return await self.redis.lpush(key, value)
    
    async def ltrim(self, key: str, start: int, end: int) -> bool:
        """
        Trim a Redis list to the specified range.
        
        Args:
            key: The Redis list key
            start: The starting index (0-based)
            end: The ending index (inclusive)
            
        Returns:
            True if successful
        """
        return await self.redis.ltrim(key, start, end)
    
    async def lrange(self, key: str, start: int, end: int) -> List[str]:
        """
        Get a range of elements from a Redis list.
        
        Args:
            key: The Redis list key
            start: The starting index (0-based)
            end: The ending index (inclusive, -1 for all elements)
            
        Returns:
            A list of values in the specified range
        """
        values = await self.redis.lrange(key, start, end)
        return values
    
    async def expire(self, key: str, seconds: int) -> bool:
        """
        Set expiration on a Redis key.
        
        Args:
            key: The Redis key
            seconds: The expiration time in seconds
            
        Returns:
            True if successful, False if the key does not exist
        """
        return await self.redis.expire(key, seconds)
    
    async def exists(self, key: str) -> bool:
        """
        Check if a key exists in Redis.
        
        Args:
            key: The Redis key
            
        Returns:
            True if successful, False if the key does not exist
        """
        return await self.redis.exists(key)

    async def scan_keys(self, pattern: str) -> List[str]:
        """
        Scan and return keys matching a given pattern.
        
        Args:
            pattern: The pattern to match keys.
            
        Returns:
            A list of keys matching the pattern.
        """
        keys = []
        async for key in self.redis.scan_iter(match=pattern):
            keys.append(key)
        return keys

    
    async def delete(self, key: str) -> bool:
        """
        Delete a key from Redis.
        
        Args:
            key: The Redis key to delete
            
        Returns:
            True if the key was deleted, False if it did not exist
        """
        return await self.redis.delete(key) > 0
