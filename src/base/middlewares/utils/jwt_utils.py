import re
from fastapi import Request

def is_path_excluded(path: str, exclude_paths: list[str]) -> bool:
    """Check if a path should be excluded from JWT verification."""
    for pattern in exclude_paths:
        if re.match(pattern, path):
            return True
    return False

def _is_localhost(self, request: Request) -> bool:
    """
    Check if the request is coming from localhost.
    
    Args:
        request: The FastAPI request object
        
    Returns:
        bool: True if the request is from localhost
    """
    host = request.headers.get("host", "")
    return host.startswith("localhost:") or host.startswith("127.0.0.1:")
    
    