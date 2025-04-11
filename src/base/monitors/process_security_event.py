from typing import Dict, Any
from src.base.scripts.security_monitor import SecurityMonitor
import logging

logger = logging.getLogger(__name__)

async def process_security_event(event: Dict[str, Any]) -> None:
    """Process a security event and update counters."""
    event_type = event.get("event_type", "unknown")
    client_ip = event.get("client_ip", "unknown")
    endpoint = event.get("path", "unknown")

    if event_type == "unauthorized_access":
        SecurityMonitor._ip_failure_counts[client_ip] += 1
        logger.info(f"Unauthorized access detected from {client_ip}")
    elif event_type == "rate_limit_violation":
        SecurityMonitor._rate_limit_violations[endpoint] += 1
        logger.info(f"Rate limit violation detected on {endpoint}")