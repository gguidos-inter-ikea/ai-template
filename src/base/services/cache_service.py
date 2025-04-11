from typing import Optional
from src.base.repositories.redis_repository import RedisRepository

class CacheService:
    """
    A service that provides cache operations using a RedisRepository.
    """
    
    def __init__(self, redis_repository: RedisRepository):
        self.redis_repository = redis_repository

    async def check_key_exists(self, key: str) -> bool:
        """
        Check if a key exists in the cache.
        """
        return await self.redis_repository.exists(key)
    
    async def scan_keys(self, pattern: str) -> list[str]:
        """
        Scan and return keys matching a given pattern.
        """
        return await self.redis_repository.scan_keys(pattern)

    async def get_value(self, key: str) -> Optional[str]:
        """
        Retrieve a value from the cache.
        """
        return await self.redis_repository.get(key)

    async def set_value(self, key: str, value: str, expiration: Optional[int] = None) -> bool:
        """
        Store a value in the cache with an optional expiration time.
        """
        return await self.redis_repository.set(key, value, expiration)
    
    async def push_value(self, key: str, value: str) -> int:
        """
        Push a value to a list in Redis.
        """
        return await self.redis_repository.lpush(key, value)
    
    async def trim_list(self, key: str, start: int, end: int) -> bool:
        """
        Trim a Redis list to a specified range.
        """
        return await self.redis_repository.ltrim(key, start, end)
    
    async def get_list(self, key: str, start: int = 0, end: int = -1) -> list[str]:
        """
        Retrieve a range of elements from a Redis list.
        """
        return await self.redis_repository.lrange(key, start, end)
    
    async def expire_key(self, key: str, seconds: int) -> bool:
        """
        Set an expiration on a key.
        """
        return await self.redis_repository.expire(key, seconds)
    
    async def delete_key(self, key: str) -> bool:
        """
        Delete a key from Redis.
        """
        return await self.redis_repository.delete(key)
