import pytest
import json
import os
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from collections import defaultdict
from src.base.scripts.security_monitor import SecurityMonitor, SecurityLogHandler

@pytest.fixture
def mock_monitor():
    """Create a mock security monitor for testing."""
    monitor = SecurityMonitor()
    monitor.alerts_enabled = True
    monitor.email_alerts_available = True
    monitor.email_alerts_enabled = True
    monitor.alert_cooldown = timedelta(minutes=0)  # No cooldown for testing
    monitor.last_alert_time = defaultdict(lambda: datetime.min)  # Initialize with datetime.min
    return monitor

@pytest.fixture
def mock_log_handler(mock_monitor):
    """Create a mock log handler for testing."""
    handler = SecurityLogHandler(monitor=mock_monitor)
    handler.setup_logging = Mock()
    return handler

@pytest.mark.asyncio
async def test_process_security_event(mock_monitor):
    """Test that alerts are sent for unauthorized access events."""
    event = {
        "event_type": "unauthorized_access",
        "client_ip": "192.168.1.100",
        "reason": "missing_auth_header",
        "timestamp": datetime.utcnow().isoformat()
    }
    
    with patch('src.base.scripts.security_monitor.send_email_alert') as mock_email:
        mock_monitor.process_security_event(event)
        mock_email.assert_called_once()

@pytest.mark.asyncio
async def test_process_error(mock_monitor):
    """Test that errors are counted and alerts are triggered."""
    with patch('src.base.scripts.security_monitor.send_email_alert') as mock_email:
        # Process multiple errors
        for _ in range(3):
            mock_monitor.process_error(
                error_type="json_decode_error",
                error_message="Invalid JSON format"
            )
        
        # Should trigger an alert after 3 errors
        mock_email.assert_called_once()

@pytest.mark.asyncio
async def test_error_window_reset(mock_monitor):
    """Test that error counts reset after the error window."""
    now = datetime.utcnow()
    past = now - timedelta(minutes=10)  # Outside the 5-minute window
    
    # Add an old error
    mock_monitor.error_count["test_error"] = 1
    mock_monitor.last_error_time["test_error"] = past
    
    # Process cleanup
    mock_monitor._cleanup_error_counts(now)
    
    # The old error should be removed
    assert "test_error" not in mock_monitor.error_count
    assert "test_error" not in mock_monitor.last_error_time

@pytest.mark.asyncio
async def test_process_security_log(mock_log_handler, mock_monitor):
    """Test processing security logs."""
    log_entry = {
        "event_type": "unauthorized_access",
        "client_ip": "192.168.1.100",
        "reason": "missing_auth_header",
        "timestamp": datetime.utcnow().isoformat()
    }
    
    with patch('src.base.scripts.security_monitor.send_email_alert') as mock_email:
        mock_monitor.process_security_event(log_entry)
        mock_email.assert_called_once()

@pytest.mark.asyncio
async def test_process_rate_limit_log(mock_log_handler, mock_monitor):
    """Test processing rate limit logs."""
    log_entry = {
        "event_type": "rate_limit",
        "client_ip": "192.168.1.100",
        "endpoint": "/api/test",
        "timestamp": datetime.utcnow().isoformat()
    }
    
    with patch('src.base.scripts.security_monitor.send_email_alert') as mock_email:
        mock_monitor.process_security_event(log_entry)
        mock_email.assert_called_once()

@pytest.mark.asyncio
async def test_send_alerts(mock_monitor):
    """Test that alerts are sent via email only."""
    event = {
        "event_type": "unauthorized_access",
        "client_ip": "192.168.1.100",
        "reason": "missing_auth_header",
        "timestamp": datetime.now().isoformat()
    }

    with patch('src.base.scripts.security_monitor.send_email_alert') as mock_email:
        mock_monitor.send_alerts(event)
        mock_email.assert_called_once()

@pytest.mark.asyncio
async def test_alert_cooldown(mock_monitor):
    """Test that alerts respect the cooldown period."""
    event = {
        "event_type": "unauthorized_access",
        "client_ip": "192.168.1.100",
        "reason": "missing_auth_header",
        "timestamp": datetime.now().isoformat()
    }

    mock_monitor.alert_cooldown = timedelta(minutes=15)  # Set cooldown period
    with patch('src.base.scripts.security_monitor.send_email_alert') as mock_email:
        # First alert should be sent
        mock_monitor.send_alerts(event, force=False)  # Explicitly set force=False
        assert mock_email.call_count == 1

        # Second alert within cooldown should not be sent
        mock_monitor.send_alerts(event, force=False)  # Explicitly set force=False
        assert mock_email.call_count == 1  # Should still be 1 since second alert is within cooldown 