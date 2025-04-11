from typing import Dict, Any
from collections import defaultdict
from src.base.scripts.security_monitor import SecurityMonitor
import logging

logger = logging.getLogger(__name__)

def process_error_event(event: Dict[str, Any]) -> None:
    """Process an error event and update counters."""
    error_module = event.get('module', 'unknown')
    error_path = event.get('path', 'unknown')
    error_message = event.get('message', '')

    if not hasattr(SecurityMonitor, '_module_error_counts'):
        SecurityMonitor._module_error_counts = defaultdict(int)
    if not hasattr(SecurityMonitor, '_path_error_counts'):
        SecurityMonitor._path_error_counts = defaultdict(int)

    SecurityMonitor._module_error_counts[error_module] += 1
    SecurityMonitor._path_error_counts[error_path] += 1
    SecurityMonitor._error_count += 1

    # Log the error pattern detection
    logger.info(f"Error pattern detected in module {error_module}: {error_message[:100]}...")