#!/usr/bin/env python
"""
Custom entrypoint for running the FastAPI application with Uvicorn.
This script configures Uvicorn to filter out logs from metrics and health endpoints.
"""
import uvicorn
import logging
import sys
import re
import os

class EndpointFilter(logging.Filter):
    """
    Filter for Uvicorn access logs that removes health and metrics endpoint logs.
    """
    def __init__(self):
        super().__init__()
        self.filtered_paths = [
            "/internal/metrics",
            "/metrics",
            "/internal/health"
        ]
        
    def filter(self, record):
        message = record.getMessage()
        for path in self.filtered_paths:
            pattern = f'"GET {path}.*'
            if re.search(pattern, message):
                return False
        return True

if __name__ == "__main__":
    # Force disable access logging via environment variable (overrides config)
    os.environ["UVICORN_ACCESS_LOG"] = "False"
    
    # Get Uvicorn's default logger and set a higher level to reduce noise
    uvicorn_logger = logging.getLogger("uvicorn")
    uvicorn_logger.setLevel(logging.WARNING)
    
    # Get Uvicorn's access logger specifically
    uvicorn_access_logger = logging.getLogger("uvicorn.access")
    
    # Add our filter to the access logger
    uvicorn_access_logger.addFilter(EndpointFilter())
    
    # Completely disable access logger for metrics endpoints
    for handler in uvicorn_access_logger.handlers:
        handler.addFilter(EndpointFilter())
    
    # Start Uvicorn with the same parameters it would normally get
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="warning",  # Set to warning to reduce logs
        access_log=False      # Disable access logs completely
    ) 