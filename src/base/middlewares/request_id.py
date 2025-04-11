from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
import uuid
import logging
from contextvars import ContextVar

# Create a context variable for request ID that can be accessed from anywhere
request_id_var: ContextVar[str] = ContextVar("request_id", default="")

# Create a filter that adds request_id to all log records
class RequestIDFilter(logging.Filter):
    """Add request_id to all log records if available."""
    
    def filter(self, record):
        # Get the request ID from the context, or use a default value
        try:
            record.request_id = request_id_var.get()
        except:
            record.request_id = "no-request-id"
        return True

# Add the filter to the root logger
root_logger = logging.getLogger()
root_logger.addFilter(RequestIDFilter())

class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Middleware to extract or set a request ID for each request.
    Makes the request ID available in log messages and response headers.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        # Extract the request ID from the headers or create a new one
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        
        # Store request ID in the request state for future use
        request.state.request_id = request_id
        
        # Store in the context variable so it can be accessed from anywhere
        token = request_id_var.set(request_id)
        
        try:
            # Continue processing the request and get the response
            response = await call_next(request)
            
            # Add the request ID to response headers
            response.headers["X-Request-ID"] = request_id
            
            return response
        finally:
            # Reset the context variable to avoid leaking between requests
            request_id_var.reset(token)