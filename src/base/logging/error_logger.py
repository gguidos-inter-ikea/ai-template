"""
Error logger module for tracking application errors.

This module provides specialized logging for errors such as unhandled exceptions,
runtime errors, and other critical issues.
"""
import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional

# Create a dedicated error logger
error_logger = logging.getLogger("error")

def log_application_error(
    error_message: str,
    exception: Optional[Exception] = None,
    additional_info: Optional[Dict[str, Any]] = None
) -> None:
    """
    Log an application error with detailed information.
    
    Args:
        error_message: A description of the error
        exception: The exception object (if available)
        additional_info: Any additional information to include in the log
    """
    # Build the log data
    log_data = {
        "timestamp": datetime.now().isoformat(),
        "event_type": "application_error",
        "log_type": "error",
        "error_message": error_message,
    }
    
    # Add exception details if provided
    if exception:
        log_data["exception_type"] = type(exception).__name__
        log_data["exception_message"] = str(exception)
    
    # Add any additional info
    if additional_info:
        log_data.update(additional_info)
    
    # Log the data as JSON
    error_logger.error(json.dumps(log_data))