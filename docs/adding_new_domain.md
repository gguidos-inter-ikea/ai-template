# Adding a New Domain

This document provides a step-by-step guide for adding a new domain to the FastAPI Microservice Boilerplate.

## Overview

The boilerplate is designed to be easily extensible with new domains. A domain represents a specific business capability or feature area of your application.

## Step 1: Create the Domain Directory Structure

First, create a new directory for your domain in `src/domains/`:

```bash
mkdir -p src/domains/your_domain/{interfaces,repositories,services}
touch src/domains/your_domain/__init__.py
touch src/domains/your_domain/interfaces/__init__.py
touch src/domains/your_domain/repositories/__init__.py
touch src/domains/your_domain/services/__init__.py
```

## Step 2: Implement the Repository Layer

The repository layer handles data access. Create a file for your repository in `src/domains/your_domain/repositories/`:

```python
# src/domains/your_domain/repositories/your_repository.py

from typing import List, Dict, Any, Optional
from src.base.infrastructure.mongoDB.mongo_client import MongoDBClient

class YourRepository:
    """
    Repository for handling your domain data operations.
    """
    
    def __init__(self, mongo_client: MongoDBClient):
        """
        Initialize the repository with dependencies.
        
        Args:
            mongo_client: MongoDB client for database operations
        """
        self.mongo_client = mongo_client
        self.collection_name = "your_collection"
    
    async def find_by_id(self, item_id: str) -> Optional[Dict[str, Any]]:
        """
        Find an item by ID.
        
        Args:
            item_id: The ID of the item to find
            
        Returns:
            The item document or None if not found
        """
        return await self.mongo_client.find_one(
            self.collection_name, 
            {"_id": item_id}
        )
    
    async def find_all(self, limit: int = 100, skip: int = 0) -> List[Dict[str, Any]]:
        """
        Find all items with pagination.
        
        Args:
            limit: Maximum number of items to return
            skip: Number of items to skip
            
        Returns:
            List of item documents
        """
        cursor = self.mongo_client.find(
            self.collection_name,
            {},
            limit=limit,
            skip=skip
        )
        return await cursor.to_list(length=limit)
    
    async def create(self, data: Dict[str, Any]) -> str:
        """
        Create a new item.
        
        Args:
            data: The data for the new item
            
        Returns:
            The ID of the created item
        """
        result = await self.mongo_client.insert_one(
            self.collection_name,
            data
        )
        return str(result.inserted_id)
    
    async def update(self, item_id: str, data: Dict[str, Any]) -> bool:
        """
        Update an existing item.
        
        Args:
            item_id: The ID of the item to update
            data: The updated data
            
        Returns:
            True if the item was updated, False otherwise
        """
        result = await self.mongo_client.update_one(
            self.collection_name,
            {"_id": item_id},
            {"$set": data}
        )
        return result.modified_count > 0
    
    async def delete(self, item_id: str) -> bool:
        """
        Delete an item.
        
        Args:
            item_id: The ID of the item to delete
            
        Returns:
            True if the item was deleted, False otherwise
        """
        result = await self.mongo_client.delete_one(
            self.collection_name,
            {"_id": item_id}
        )
        return result.deleted_count > 0
```

## Step 3: Implement the Service Layer

The service layer contains business logic. Create a file for your service in `src/domains/your_domain/services/`:

```python
# src/domains/your_domain/services/your_service.py

from typing import List, Dict, Any, Optional
import json
from src.domains.your_domain.repositories.your_repository import YourRepository
from src.base.infrastructure.redis.redis_client import RedisClient

class YourService:
    """
    Service for handling your domain business logic.
    """
    
    def __init__(self, repository: YourRepository, redis_client: RedisClient):
        """
        Initialize the service with dependencies.
        
        Args:
            repository: Repository for data operations
            redis_client: Redis client for caching
        """
        self.repository = repository
        self.redis_client = redis_client
        self.cache_prefix = "your_domain:"
        self.cache_ttl = 3600  # 1 hour
    
    async def get_by_id(self, item_id: str) -> Optional[Dict[str, Any]]:
        """
        Get an item by ID with caching.
        
        Args:
            item_id: The ID of the item to get
            
        Returns:
            The item data or None if not found
        """
        # Try to get from cache first
        cache_key = f"{self.cache_prefix}{item_id}"
        cached_data = await self.redis_client.get(cache_key)
        
        if cached_data:
            return json.loads(cached_data)
        
        # If not in cache, get from repository
        item = await self.repository.find_by_id(item_id)
        
        if item:
            # Cache the result
            await self.redis_client.set(
                cache_key, 
                json.dumps(item), 
                expire=self.cache_ttl
            )
        
        return item
    
    async def get_all(self, limit: int = 100, skip: int = 0) -> List[Dict[str, Any]]:
        """
        Get all items with pagination.
        
        Args:
            limit: Maximum number of items to return
            skip: Number of items to skip
            
        Returns:
            List of item data
        """
        return await self.repository.find_all(limit=limit, skip=skip)
    
    async def create_item(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new item.
        
        Args:
            data: The data for the new item
            
        Returns:
            The created item with ID
        """
        item_id = await self.repository.create(data)
        return {**data, "id": item_id}
    
    async def update_item(self, item_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update an existing item.
        
        Args:
            item_id: The ID of the item to update
            data: The updated data
            
        Returns:
            The updated item or None if not found
        """
        # Check if item exists
        existing = await self.repository.find_by_id(item_id)
        if not existing:
            return None
        
        # Update the item
        success = await self.repository.update(item_id, data)
        if not success:
            return None
        
        # Invalidate cache
        cache_key = f"{self.cache_prefix}{item_id}"
        await self.redis_client.delete(cache_key)
        
        # Return updated item
        return {**data, "id": item_id}
    
    async def delete_item(self, item_id: str) -> bool:
        """
        Delete an item.
        
        Args:
            item_id: The ID of the item to delete
            
        Returns:
            True if the item was deleted, False otherwise
        """
        success = await self.repository.delete(item_id)
        
        if success:
            # Invalidate cache
            cache_key = f"{self.cache_prefix}{item_id}"
            await self.redis_client.delete(cache_key)
        
        return success
```

## Step 4: Create the API Interface

Create a file for your API router in `src/domains/your_domain/interfaces/`:

```python
# src/domains/your_domain/interfaces/your_router.py

from fastapi import APIRouter, Depends, HTTPException, Request, status
from typing import List, Dict, Any
from dependency_injector.wiring import inject
from src.domains.your_domain.services.your_service import YourService

router = APIRouter()

@router.get("/{item_id}", response_model=Dict[str, Any])
async def get_item(
    request: Request,
    item_id: str,
    your_service: YourService = Depends(lambda: request.app.container.your_service())
):
    """
    Get an item by ID.
    """
    item = await your_service.get_by_id(item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with ID {item_id} not found"
        )
    return item

@router.get("/", response_model=List[Dict[str, Any]])
async def get_items(
    request: Request,
    limit: int = 100,
    skip: int = 0,
    your_service: YourService = Depends(lambda: request.app.container.your_service())
):
    """
    Get all items with pagination.
    """
    return await your_service.get_all(limit=limit, skip=skip)

@router.post("/", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def create_item(
    request: Request,
    data: Dict[str, Any],
    your_service: YourService = Depends(lambda: request.app.container.your_service())
):
    """
    Create a new item.
    """
    return await your_service.create_item(data)

@router.put("/{item_id}", response_model=Dict[str, Any])
async def update_item(
    request: Request,
    item_id: str,
    data: Dict[str, Any],
    your_service: YourService = Depends(lambda: request.app.container.your_service())
):
    """
    Update an existing item.
    """
    updated = await your_service.update_item(item_id, data)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with ID {item_id} not found"
        )
    return updated

@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(
    request: Request,
    item_id: str,
    your_service: YourService = Depends(lambda: request.app.container.your_service())
):
    """
    Delete an item.
    """
    success = await your_service.delete_item(item_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with ID {item_id} not found"
        )
    return None
```

## Step 5: Setup the Domain Container

Create a dependency injection container for your domain:

```python
# src/domains/your_domain/di_container.py

from dependency_injector import containers, providers
from src.base.dependencies.di_container import Container as BaseContainer
from src.domains.your_domain.repositories.your_repository import YourRepository
from src.domains.your_domain.services.your_service import YourService

class YourDomainContainer(containers.DeclarativeContainer):
    """
    Container for your domain that extends the base container.
    """
    # Reuse the base container's configuration
    config = providers.Configuration()
    
    # Import dependencies from the base container
    mongo_client = providers.Dependency()
    redis_client = providers.Dependency()
    
    # Domain-specific repositories
    your_repository = providers.Singleton(
        YourRepository,
        mongo_client=mongo_client
    )
    
    # Domain-specific services
    your_service = providers.Singleton(
        YourService,
        repository=your_repository,
        redis_client=redis_client
    )


def extend_container(base_container: BaseContainer) -> BaseContainer:
    """
    Extends the base container with domain-specific dependencies.
    
    Args:
        base_container: The base container to extend
        
    Returns:
        The extended container
    """
    # Create the domain container
    domain_container = YourDomainContainer()
    
    # Wire the domain container with the base container
    domain_container.mongo_client.override(base_container.mongo_client)
    domain_container.redis_client.override(base_container.redis_client)
    
    # Add domain-specific providers to the base container
    setattr(base_container, 'your_repository', domain_container.your_repository)
    setattr(base_container, 'your_service', domain_container.your_service)
    
    return base_container
```

## Step 6: Register Domain Routes

Update the domain's `__init__.py` file to register routes:

```python
# src/domains/your_domain/__init__.py

from fastapi import FastAPI
from src.domains.your_domain.interfaces.your_router import router as your_router

def register_routes(app: FastAPI):
    """
    Register routes for your domain.
    
    Args:
        app: The FastAPI application
    """
    app.include_router(
        your_router,
        prefix="/api/v1/your-domain",
        tags=["Your Domain"]
    )
```

## Step 7: Register the Domain with the Main Application

### 1. Update `src/domains/__init__.py`:

```python
# Add import for your domain
from src.domains.your_domain.di_container import extend_container as extend_with_your_domain

def initialize_domains(container: BaseContainer) -> BaseContainer:
    # Add your domain to the initialization
    container = extend_with_example_domain(container)
    container = extend_with_your_domain(container)  # Add this line
    
    return container
```

### 2. Update `src/domains/routes.py`:

```python
# Add import for your domain
from src.domains.your_domain import register_routes as register_your_domain_routes

def register_domain_routes(app: FastAPI):
    # Add your domain to the route registration
    register_example_routes(app)
    register_your_domain_routes(app)  # Add this line
```

## Step 8: Test Your New Domain

1. Start the application:

```bash
docker-compose up
# or
uvicorn src.main:app --reload
```

2. Test the API endpoints:

```bash
# Create an item
curl -X POST "http://localhost:8000/api/v1/your-domain/" \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Item", "description": "This is a test item"}'

# Get all items
curl -X GET "http://localhost:8000/api/v1/your-domain/"

# Get an item by ID
curl -X GET "http://localhost:8000/api/v1/your-domain/{item_id}"

# Update an item
curl -X PUT "http://localhost:8000/api/v1/your-domain/{item_id}" \
  -H "Content-Type: application/json" \
  -d '{"name": "Updated Item", "description": "This item has been updated"}'

# Delete an item
curl -X DELETE "http://localhost:8000/api/v1/your-domain/{item_id}"
```

## Best Practices

1. **Follow the Domain Structure**: Keep the repository, service, and interface layers separate
2. **Add Validation**: Use Pydantic models for request and response validation
3. **Implement Caching**: Use Redis for caching frequently accessed data
4. **Add Unit Tests**: Create unit tests for your domain components
5. **Document Endpoints**: Add detailed docstrings to your API endpoints
6. **Use Rate Limiting**: Apply rate limiting to sensitive endpoints
7. **Add Logging**: Include appropriate logging in your domain components

## Conclusion

You have now added a new domain to the FastAPI Microservice Boilerplate. This domain encapsulates a specific business capability and follows the clean architecture principles of the boilerplate. 