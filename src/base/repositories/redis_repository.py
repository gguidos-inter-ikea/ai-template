# src/base/repositories/redis_repository.py
from abc import ABC, abstractmethod
from typing import List, Optional

class RedisRepository(ABC):
    """Abstract interface for Redis operations"""
    
    @abstractmethod
    async def get(self, key: str) -> Optional[str]:
        """Get a value by key"""
        pass
        
    @abstractmethod
    async def set(self, key: str, value: str, expiration: Optional[int] = None) -> bool:
        """Set a key-value pair with optional expiration"""
        pass
    
    @abstractmethod
    async def lpush(self, key: str, value: str) -> int:
        """Push a value to the left of a list"""
        pass
    
    @abstractmethod
    async def ltrim(self, key: str, start: int, end: int) -> bool:
        """Trim a list to specified range"""
        pass
    
    @abstractmethod
    async def lrange(self, key: str, start: int, end: int) -> List[str]:
        """Get a range of list elements"""
        pass
    
    @abstractmethod
    async def expire(self, key: str, seconds: int) -> bool:
        """Set expiration on a key"""
        pass

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """
        Check if a key exists in Redis.
        """
        pass

    @abstractmethod
    async def scan_keys(self, pattern:str) -> List[str]:
        """Scan and return keys matching a given pattern."""
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete a key"""
        pass