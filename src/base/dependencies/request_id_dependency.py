from fastapi import Request

async def get_request_id(request: Request) -> str:
    """Dependency to get the request ID from the request state."""
    
    return request.state.request_id