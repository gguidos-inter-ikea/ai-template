"""
Security logger module for tracking security-related events.

This module provides specialized logging for security events such as
unauthorized access attempts, authentication failures, and other
security-related incidents.
"""
import logging
import json
from datetime import datetime
from fastapi import Request
from typing import Dict, Any, Optional

# Create a dedicated security logger
security_logger = logging.getLogger("security")

async def log_unauthorized_access(
    request: Request,
    reason: str,
    additional_info: Optional[Dict[str, Any]] = None
) -> None:
    """
    Log an unauthorized access attempt with detailed information.
    
    Args:
        request: The FastAPI request object
        reason: The reason for the unauthorized access (missing token, invalid token, etc.)
        additional_info: Any additional information to include in the log
    """
    client_host = request.client.host if request.client else "unknown"
    
    # Build the log data
    log_data = {
        "timestamp": datetime.now().isoformat(),
        "event_type": "unauthorized_access",
        "log_type": "security",
        "client_ip": client_host,
        "path": request.url.path,
        "method": request.method,
        "reason": reason,
        "user_agent": request.headers.get("User-Agent", "unknown"),
        "referer": request.headers.get("Referer", "none"),
        "x_forwarded_for": request.headers.get("X-Forwarded-For", "none"),
    }
    
    # Add any additional info
    if additional_info:
        log_data.update(additional_info)
    
    # Log the data as JSON
    security_logger.warning(json.dumps(log_data))
    
    # Instead of direct monitor call, use a delayed import to avoid circular dependency
    try:
        from src.base.scripts.security_monitor import monitor
        # Send the event to the security monitor
        import asyncio
        asyncio.create_task(monitor.process_security_event(log_data))
    except (ImportError, AttributeError) as e:
        security_logger.error(f"Could not send event to security monitor: {str(e)}") 