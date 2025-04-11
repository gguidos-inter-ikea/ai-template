# Dependency Injection

This document explains how dependency injection is implemented and used in the FastAPI Microservice Boilerplate.

## Overview

Dependency Injection (DI) is a design pattern that allows for better code organization, testability, and maintainability. In this boilerplate, we use the `dependency-injector` package to implement DI.

The key benefits of using DI in this project are:

1. **Decoupling**: Components are decoupled from their dependencies
2. **Testability**: Dependencies can be easily mocked for testing
3. **Flexibility**: Dependencies can be swapped without changing the dependent code
4. **Maintainability**: Dependencies are managed in a central location

## Container Structure

The DI system is organized into containers:

### Base Container

The base container (`src/base/dependencies/di_container.py`) provides infrastructure components:

```python
class Container(containers.DeclarativeContainer):
    """
    A dependency injection container that loads configuration and provides
    singletons/factories for the applications needs.
    """
    config = providers.Configuration()

    # MongoDB client
    mongo_client = providers.Singleton(
        MongoDBClient,
        db_uri=settings.mongodb_uri,
        db_name=settings.mongodb_dbname,
    )

    redis_client = providers.Singleton(
        RedisClient,
        host=settings.redis_host,
        port=settings.redis_port,
        db=settings.redis_db
    )
    
    def init_resources(self):
        """
        Initialize any resources needed by the container.
        This method is called during application startup.
        """
        # Nothing to initialize here, but subclasses may override this method
        pass
```

### Domain Containers

Domain containers extend the base container with domain-specific components:

```python
class ExampleDomainContainer(containers.DeclarativeContainer):
    """
    Container for the Example domain that extends the base container.
    This allows adding domain-specific dependencies without modifying the base container.
    """
    # Reuse the base container's configuration
    config = providers.Configuration()
    
    # Import dependencies from the base container
    mongo_client = providers.Dependency()
    redis_client = providers.Dependency()
    
    # Domain-specific repositories
    example_repository = providers.Singleton(
        ExampleRepository,
        mongo_client=mongo_client
    )
    
    # Domain-specific services
    example_service = providers.Singleton(
        ExampleService,
        repository=example_repository,
        redis_client=redis_client
    )
```

## Container Extension

Domain containers are wired to the base container using the `extend_container` function:

```python
def extend_container(base_container: BaseContainer) -> BaseContainer:
    """
    Extends the base container with domain-specific dependencies.
    
    Args:
        base_container: The base container to extend
        
    Returns:
        The extended container
    """
    # Create the domain container
    domain_container = ExampleDomainContainer()
    
    # Wire the domain container with the base container
    domain_container.mongo_client.override(base_container.mongo_client)
    domain_container.redis_client.override(base_container.redis_client)
    
    # Add domain-specific providers to the base container
    setattr(base_container, 'example_repository', domain_container.example_repository)
    setattr(base_container, 'example_service', domain_container.example_service)
    
    return base_container
```

## Container Initialization

The container is initialized in `main.py`:

```python
# Create and configure the dependency injection container
container = Container()

# Initialize resources (if needed)
if hasattr(container, 'init_resources'):
    container.init_resources()

# Initialize domain-specific containers
container = initialize_domains(container)

# Attach the container to the app
app.container = container
```

## Using Dependencies in FastAPI Endpoints

Dependencies are injected into FastAPI endpoints using the `Depends` function:

```python
@router.get("/{example_id}", response_model=Dict[str, Any])
@inject
async def get_example(
    request: Request,
    example_id: str,
    example_service: ExampleService = Depends(lambda: request.app.container.example_service())
):
    """
    Get an example by ID.
    """
    example = await example_service.get_by_id(example_id)
    if not example:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Example with ID {example_id} not found"
        )
    return example
```

## Adding New Dependencies

To add a new dependency:

1. **Define the dependency**: Create a new class or function
2. **Add it to a container**: Add a provider to the appropriate container
3. **Wire it up**: If it's a domain-specific dependency, wire it to the base container
4. **Use it**: Inject it into the components that need it

### Example: Adding a New Service

```python
# 1. Define the service
class NewService:
    def __init__(self, repository, redis_client):
        self.repository = repository
        self.redis_client = redis_client
    
    async def do_something(self):
        # Implementation
        pass

# 2. Add it to the domain container
class MyDomainContainer(containers.DeclarativeContainer):
    # ...
    
    new_service = providers.Singleton(
        NewService,
        repository=example_repository,
        redis_client=redis_client
    )

# 3. Wire it up in the extend_container function
def extend_container(base_container):
    # ...
    
    setattr(base_container, 'new_service', domain_container.new_service)
    
    return base_container

# 4. Use it in an endpoint
@router.get("/new-endpoint")
@inject
async def new_endpoint(
    request: Request,
    new_service: NewService = Depends(lambda: request.app.container.new_service())
):
    result = await new_service.do_something()
    return {"result": result}
```

## Testing with Dependency Injection

DI makes testing easier by allowing dependencies to be mocked:

```python
def test_example_service():
    # Create a mock repository
    mock_repository = MagicMock()
    mock_repository.find_by_id.return_value = {"id": "123", "name": "Test"}
    
    # Create a mock Redis client
    mock_redis = MagicMock()
    
    # Create the service with mocked dependencies
    service = ExampleService(repository=mock_repository, redis_client=mock_redis)
    
    # Test the service
    result = await service.get_by_id("123")
    
    # Assert the result
    assert result["name"] == "Test"
    
    # Verify the repository was called
    mock_repository.find_by_id.assert_called_once_with("123")
```

## Best Practices

1. **Keep containers focused**: Each container should have a single responsibility
2. **Use singletons for stateful dependencies**: Use `providers.Singleton` for database clients, repositories, etc.
3. **Use factories for stateless dependencies**: Use `providers.Factory` for request-scoped dependencies
4. **Avoid circular dependencies**: Design your components to avoid circular dependencies
5. **Document dependencies**: Clearly document what each component depends on
6. **Test with mocked dependencies**: Use mocks to test components in isolation 