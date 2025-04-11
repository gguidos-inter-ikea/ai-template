import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import Request, HTTPException

@pytest.mark.asyncio
async def test_simple_rate_limit():
    """
    A simpler test to verify basic rate limiting functionality.
    """
    # Use direct testing of the rate limiter function
    from base.security.rate_limiter import create_rate_limiter, ip_identifier, api_key_identifier, CombinedRateLimiter
    
    # Create a rate limiter with a specific limit
    limiter = create_rate_limiter(times=3, seconds=10)
    
    # Verify it has the expected properties
    assert hasattr(limiter, "times")
    assert limiter.times == 3
    
    # Test IP identifier
    mock_request = MagicMock(spec=Request)
    mock_request.client.host = "127.0.0.1"
    mock_request.headers = {}
    
    identifier = ip_identifier(mock_request)
    assert identifier == "ip:127.0.0.1"
    
    # Test with X-Forwarded-For header
    mock_request.headers = {"X-Forwarded-For": "192.168.1.1, 10.0.0.1"}
    identifier = ip_identifier(mock_request)
    assert identifier == "ip:192.168.1.1"
    
    # Test API key identifier
    mock_request.headers = {}
    identifier = api_key_identifier(mock_request)
    assert identifier == "api_key:anonymous"
    
    mock_request.headers = {"X-API-Key": "test-api-key"}
    identifier = api_key_identifier(mock_request)
    assert identifier == "api_key:test-api-key"
    
    # Test combining limiters
    # Create mock limiters
    limiter1 = AsyncMock()
    limiter2 = AsyncMock()
    
    # Create combined limiter
    combined = CombinedRateLimiter([limiter1, limiter2])
    
    # Configure mocks
    limiter1.return_value = True
    limiter2.return_value = True
    
    # Test successful case (both limiters pass)
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