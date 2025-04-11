"""
Logging override configuration to suppress metrics and health endpoint logs.
This file is loaded after the main logging configuration to apply specific overrides.
"""
import logging

class MetricsEndpointFilter(logging.Filter):
    """
    Filter to exclude specific endpoints from logs.
    """
    def __init__(self):
        super().__init__()
        self.excluded_paths = [
            "/internal/metrics",
            "/metrics",
            "/internal/health"
        ]
        
    def filter(self, record):
        # Skip filtering if it's not an access log
        if not hasattr(record, 'args') or not isinstance(record.args, tuple) or len(record.args) < 3:
            return True
            
        try:
            # For Uvicorn access logs, the path is in the third argument as part of a string like 'GET /path HTTP/1.1'
            request_info = record.args[2]
            for path in self.excluded_paths:
                if f" {path}" in request_info or f" {path}/" in request_info:
                    return False  # Don't log this record
        except (IndexError, AttributeError):
            pass
            
        return True  # Log this record

def apply_logging_overrides():
    """
    Apply specific overrides to the logging configuration.
    This is called after the main logging config is loaded.
    """
    # Get Uvicorn's access logger
    uvicorn_access_logger = logging.getLogger("uvicorn.access")
    
    # Set its level to WARNING to hide INFO logs
    uvicorn_access_logger.setLevel(logging.WARNING)
    
    # Add our filter to exclude metrics endpoint logs
    metrics_filter = MetricsEndpointFilter()
    uvicorn_access_logger.addFilter(metrics_filter)
    
    # Apply the filter to all handlers as well
    for handler in uvicorn_access_logger.handlers:
        handler.addFilter(metrics_filter)
    
    # Also set the uvicorn error logger to a higher level
    uvicorn_error_logger = logging.getLogger("uvicorn.error")
    uvicorn_error_logger.setLevel(logging.ERROR) 