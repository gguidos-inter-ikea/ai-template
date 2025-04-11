from functools import wraps
from fastapi import Request, HTTPException
from src.base.middlewares.utils.session_utils import get_session_key
import logging

logger = logging.getLogger(__name__)

def extract_domain_from_path(path: str) -> str:
    """
    Extracts the domain from the URL path.
    
    This assumes your URL pattern is like:
      /api/v1/{domain}/endpoint
    and will return '{domain}'.
    """
    parts = path.strip("/").split("/")
    if len(parts) >= 3:
        return parts[2]
    # Fallback: if the pattern is different, return the last segment
    return parts[-1] if parts else ""
    
def session_based(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Try to extract the request from the endpoint arguments.
        # FastAPI automatically passes the Request if declared in the endpoint parameters.

        request: Request = kwargs.get("request")
        if not request:
            # Alternatively, you may iterate through args to find a Request instance.
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
        if not request:
            raise HTTPException(status_code=500, detail="Request object not found.")

        # Extract session key logic from the Authorization header.
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            jwt_token = auth_header.replace("Bearer ", "")
            session_key = get_session_key(jwt_token=jwt_token, domain=extract_domain_from_path(request.url.path))
            # Attach the session key to the request state for later use.
            request.app.state.session_key = session_key
            logger.info(f"Session key generated: {session_key}")

        else:
            # Handle missing or invalid auth headers.
            raise HTTPException(status_code=401, detail="Missing or invalid Authorization header.")

        # Continue with the original endpoint function.
        return await func(*args, **kwargs)
    return wrapper