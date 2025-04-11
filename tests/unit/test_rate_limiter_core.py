import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi import Request, HTTPException
from base.security.rate_limiter import (
    create_rate_limiter,
    ip_identifier,
    api_key_identifier,
    CombinedRateLimiter,
    rate_limited
)

@pytest.fixture
def mock_request():
    """Create a mock FastAPI request object."""
    mock = MagicMock(spec=Request)
    mock.client.host = "127.0.0.1"
    mock.headers = {}
    return mock

def test_ip_identifier(mock_request):
    """Test that ip_identifier correctly extracts the client IP."""
    # Test with direct client IP
    identifier = ip_identifier(mock_request)
    assert identifier == "ip:127.0.0.1"
    
    # Test with X-Forwarded-For header
    mock_request.headers = {"X-Forwarded-For": "192.168.1.1, 10.0.0.1"}
    identifier = ip_identifier(mock_request)
    assert identifier == "ip:192.168.1.1"

def test_api_key_identifier(mock_request):
    """Test that api_key_identifier correctly extracts the API key."""
    # Test with no API key (should use "anonymous")
    identifier = api_key_identifier(mock_request)
    assert identifier == "api_key:anonymous"
    
    # Test with API key
    mock_request.headers = {"X-API-Key": "test-api-key"}
    identifier = api_key_identifier(mock_request)
    assert identifier == "api_key:test-api-key"

@pytest.mark.asyncio
async def test_create_rate_limiter():
    """Test that create_rate_limiter properly configures a RateLimiter."""
    # Create a limiter with default identifier
    limiter = create_rate_limiter(times=10, seconds=30)
    # Check that the limiter is created properly
    assert hasattr(limiter, "times")
    assert limiter.times == 10
    # We can't directly check seconds as it's not a public attribute, 
    # but we can ensure the limiter is callable
    assert callable(limiter)
    
    # Create a limiter with custom identifier
    custom_identifier = lambda req: "custom:id"
    limiter_with_identifier = create_rate_limiter(times=5, seconds=60, identifier=custom_identifier)
    assert hasattr(limiter_with_identifier, "times")
    assert limiter_with_identifier.times == 5
    assert limiter_with_identifier.identifier == custom_identifier

@pytest.mark.asyncio
async def test_combined_rate_limiter():
    """Test that CombinedRateLimiter applies all limiters correctly."""
    # Create mock limiters
    limiter1 = AsyncMock()
    limiter2 = AsyncMock()
    
    # Create combined limiter
    combined = CombinedRateLimiter([limiter1, limiter2])
    
    # Create mock request
    mock_request = MagicMock()
    
    # Test successful case (both limiters pass)
    limiter1.return_value = True
    limiter2.return_value = True
    result = await combined(mock_request)
    assert result is True
    limiter1.assert_called_once_with(mock_request)
    limiter2.assert_called_once_with(mock_request)
    
    # Reset mocks
    limiter1.reset_mock()
    limiter2.reset_mock()
    
    # Test failure case (first limiter raises exception)
    limiter1.side_effect = HTTPException(status_code=429, detail="Too Many Requests")
    
    with pytest.raises(HTTPException) as exc_info:
        await combined(mock_request)
    
    assert exc_info.value.status_code == 429
    assert exc_info.value.detail == "Too Many Requests"
    limiter1.assert_called_once_with(mock_request)
    # Second limiter shouldn't be called if first one fails
    limiter2.assert_not_called()

@pytest.mark.asyncio
async def test_rate_limited_decorator():
    """Test that rate_limited decorator applies rate limiting correctly."""
    # Create a mock endpoint function
    async def mock_endpoint():
        return {"message": "Success"}
    
    # Create a mock RateLimiter
    mock_limiter = AsyncMock()
    
    # Apply decorator
    decorated = rate_limited(limiter=mock_limiter)(mock_endpoint)
    
    # Verify the decorator adds the dependency correctly
    assert hasattr(decorated, "__dependencies__")
    assert len(decorated.__dependencies__) == 1
    
    # The actual dependency testing would be done in integration tests
    # since FastAPI handles dependency injection during request processing 