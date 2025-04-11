"""
Tests for dependency injection container initialization and wiring.
"""
import pytest
from src.base.dependencies.di_container import Container
from src.base.dependencies.rate_limiter_dependencies import (
    get_standard_api_rate_limiter,
    get_standard_write_rate_limiter,
    get_standard_read_rate_limiter,
    get_moderate_rate_limiter,
)
from dependency_injector.wiring import Provide
from unittest.mock import Mock

def test_container_initialization():
    """Test that the DI container initializes properly with auto wiring."""
    # Create a container instance
    container = Container()
    
    # Check that essential components are available
    assert container.mongo_client is not None
    assert container.redis_client is not None
    assert container.rate_limiter_factory is not None
    assert container.standard_api_rate_limiter is not None
    assert container.standard_write_rate_limiter is not None
    assert container.standard_read_rate_limiter is not None


def test_container_providers():
    """Test that the container providers are callable."""
    # Create a container instance
    container = Container()
    
    # Get providers and verify they're callable
    assert callable(container.rate_limiter_factory)
    assert callable(container.standard_api_rate_limiter)
    assert callable(container.standard_write_rate_limiter)
    assert callable(container.standard_read_rate_limiter)


@pytest.mark.parametrize("provider_name", [
    "mongo_client",
    "redis_client",
    "rate_limiter_factory",
    "standard_api_rate_limiter",
    "standard_write_rate_limiter",
    "standard_read_rate_limiter",
])
def test_container_provider_access(provider_name):
    """Test that all essential providers can be accessed."""
    container = Container()
    provider = getattr(container, provider_name)
    assert provider is not None 