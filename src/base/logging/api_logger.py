"""
API Logger
"""
import logging
import time
from functools import wraps
from typing import Callable, Any

api_logger = logging.getLogger("external_api")

def log_external_api(service_name: str) -> Callable:
    """Decorator to log external API calls"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract endpoint information
            endpoint = kwargs.get("endpoint", "unknown")
            method = kwargs.get("method", "GET")
            
            # Generate a call ID
            call_id = f"{service_name}-{time.time()}"
            
            # Log the API call start
            start_time = time.time()
            
            api_logger.info(
                f"External API Call: {service_name} - {method} {endpoint}",
                extra={
                    "call_id": call_id,
                    "service": service_name,
                    "method": method,
                    "endpoint": endpoint,
                    "status": "started"
                }
            )
            
            try:
                # Execute the API call
                result = await func(*args, **kwargs)
                
                # Calculate duration
                duration_ms = (time.time() - start_time) * 1000
                
                # Log successful API call
                api_logger.info(
                    f"External API Response: {service_name} - {method} {endpoint}",
                    extra={
                        "call_id": call_id,
                        "service": service_name,
                        "method": method,
                        "endpoint": endpoint,
                        "status": "success",
                        "duration_ms": duration_ms,
                        "status_code": getattr(result, "status_code", None)
                    }
                )
                
                return result
                
            except Exception as e:
                # Calculate duration
                duration_ms = (time.time() - start_time) * 1000
                
                # Log failed API call
                api_logger.error(
                    f"External API Error: {service_name} - {method} {endpoint}",
                    extra={
                        "call_id": call_id,
                        "service": service_name,
                        "method": method,
                        "endpoint": endpoint,
                        "status": "error",
                        "duration_ms": duration_ms,
                        "error": str(e)
                    }
                )
                
                # Re-raise the exception
                raise
                
        return wrapper
    return decorator
