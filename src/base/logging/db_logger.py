"""
Database Logger
"""
import logging
import time
from functools import wraps
from typing import Callable, Any

db_logger = logging.getLogger("database")

def log_query(func: Callable) -> Callable:
    """Decorator to log database queries and their performance"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Extract query information from args or kwargs
        collection = args[0].collection if args else kwargs.get("collection", "unknown")
        operation = func.__name__
        
        # Log the query start
        start_time = time.time()
        
        try:
            # Execute the query
            result = await func(*args, **kwargs)
            
            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000
            
            # Log successful query
            db_logger.debug(
                f"DB Query: {operation} on {collection}",
                extra={
                    "operation": operation,
                    "collection": str(collection),
                    "duration_ms": duration_ms,
                    "success": True
                }
            )
            
            return result
            
        except Exception as e:
            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000
            
            # Log failed query
            db_logger.error(
                f"DB Query Error: {operation} on {collection}",
                extra={
                    "operation": operation,
                    "collection": str(collection),
                    "duration_ms": duration_ms,
                    "success": False,
                    "error": str(e)
                }
            )
            
            # Re-raise the exception
            raise
            
    return wrapper
