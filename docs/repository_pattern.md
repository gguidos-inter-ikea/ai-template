# Repository Pattern

This document explains how the repository pattern is implemented and used in the application for abstracting data access.

## Overview

The repository pattern provides a clean separation between the data access layer and the business logic of the application. It offers several benefits:

- **Abstraction**: Hides the details of data storage and retrieval
- **Testability**: Makes it easier to mock data access for testing
- **Flexibility**: Allows changing the underlying storage without affecting business logic
- **Consistency**: Provides a uniform API for working with different data sources

## Redis Repository

The application implements a Redis repository to abstract Redis operations, making it easier to use Redis throughout the application.

### Interface

The `RedisRepository` interface defines the contract for Redis operations:

```python
# src/base/repositories/redis_repository.py
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Union

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
    async def delete(self, key: str) -> bool:
        """Delete a key"""
        pass
```

### Implementation

The implementation uses `aioredis` for asynchronous Redis operations:

```python
# src/base/repositories/redis_impl.py
from typing import List, Dict, Any, Optional, Union
import aioredis
from src.base.repositories.redis_repository import RedisRepository

class RedisRepositoryImpl(RedisRepository):
    """Implementation of the RedisRepository interface"""
    
    def __init__(self, redis_client: aioredis.Redis):
        self.redis = redis_client
    
    async def get(self, key: str) -> Optional[str]:
        value = await self.redis.get(key)
        return value
    
    async def set(self, key: str, value: str, expiration: Optional[int] = None) -> bool:
        if expiration:
            return await self.redis.set(key, value, ex=expiration)
        return await self.redis.set(key, value)
    
    # Other method implementations...
```

### Dependency Injection

The Redis repository is registered in the dependency injection container:

```python
# src/base/dependencies/di_container.py
redis_client = providers.Resource(
    aioredis.from_url,
    url=settings.redis_url or f"redis://{settings.redis_host}:{settings.redis_port}/{settings.redis_db}",
    password=settings.redis_password,
    encoding="utf-8",
    decode_responses=True,
)

redis_repository = providers.Singleton(
    RedisRepositoryImpl,
    redis_client=redis_client
)
```

### Usage in Services

The repository is injected into services using the dependency injection system:

```python
from dependency_injector.wiring import inject, Provide
from src.base.dependencies.di_container import Container
from src.base.repositories.redis_repository import RedisRepository

class CacheService:
    @inject
    def __init__(self, redis_repository: RedisRepository = Provide[Container.redis_repository]):
        self.redis = redis_repository
        
    async def cache_data(self, key: str, data: str, ttl: int = 3600):
        await self.redis.set(key, data, expiration=ttl)
```

## MongoDB Repository

The application also implements a MongoDB repository pattern for database operations.

### Base Repository

The base repository provides common operations for MongoDB collections:

```python
class BaseRepository:
    def __init__(self, collection):
        self.collection = collection
    
    async def find_by_id(self, id):
        return await self.collection.find_one({"_id": id})
    
    async def find_all(self, query=None, limit=100, skip=0):
        cursor = self.collection.find(query or {})
        cursor = cursor.skip(skip).limit(limit)
        return await cursor.to_list(length=limit)
    
    # Other methods like create(), update(), delete()...
```

### Domain-Specific Repositories

Domain-specific repositories extend the base repository:

```python
class UserRepository(BaseRepository):
    def __init__(self, mongo_client):
        self.collection = mongo_client.get_collection("users")
        
    async def find_by_email(self, email):
        return await self.collection.find_one({"email": email})
        
    async def find_active_users(self):
        return await self.find_all({"status": "active"})
```

## Benefits of Using Repositories

1. **Clean API**: Services only need to know about the repository interface, not about the underlying data store
2. **Consistent error handling**: Repositories can provide consistent error handling for data operations
3. **Database independence**: Changing the database doesn't require changing business logic
4. **Simpler transactions**: Repositories can abstract transaction management
5. **Better testability**: Easy to mock repositories for unit testing

## Logging Database Operations

Database operations are logged using the `db_logger` decorator:

```python
from src.base.logging.db_logger import log_query

class UserRepository(BaseRepository):
    @log_query
    async def find_by_email(self, email):
        return await self.collection.find_one({"email": email})
```

## Testing With Repositories

Repositories make testing easier by allowing you to mock the data layer:

```python
# In tests
async def test_user_service():
    # Create a mock repository
    mock_repo = AsyncMock(spec=UserRepository)
    mock_repo.find_by_id.return_value = {"_id": "123", "name": "Test User"}
    
    # Inject the mock into the service
    service = UserService(repository=mock_repo)
    
    # Test the service
    user = await service.get_user("123")
    assert user["name"] == "Test User"
    mock_repo.find_by_id.assert_called_once_with("123")
``` 