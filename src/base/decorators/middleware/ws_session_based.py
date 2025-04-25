from functools import wraps
from fastapi import WebSocket, Request
from src.base.middlewares.utils.session_utils import get_session_key
import logging

logger = logging.getLogger(__name__)

def session_based_ws(on_ready=None, inject_request=False):
    def decorator(func):
        @wraps(func)
        async def wrapper(websocket: WebSocket, *args, **kwargs):
            await websocket.accept()
            
            token = websocket.headers.get("Authorization", "")
            commander_flag = websocket.headers.get("commander", "false").lower() == "true"
            signature_text = websocket.headers.get("signature", "")
            websocket.scope["commander"] = commander_flag
            websocket.scope["signature"] = signature_text
            
            if token.startswith("Bearer "):
                jwt_token = token.replace("Bearer ", "")
                domain = extract_domain_from_path(websocket.url.path)
                session_key = get_session_key(jwt_token=jwt_token, domain=domain)
                websocket.scope["session_key"] = session_key
                logger.info(f"[🔐 WS SESSION] Session key resolved: {session_key}")

                if on_ready:
                    await on_ready(websocket, session_key)

                # Optional Request injection
                if inject_request:
                    request = Request(websocket.scope)
                    return await func(websocket, request, *args, **kwargs)

                return await func(websocket, *args, **kwargs)
            else:
                await websocket.send_text("[🚫 Joshu-A] Invalid or missing token. Disconnecting...")
                await websocket.close(code=1008)
        return wrapper
    return decorator


def extract_domain_from_path(path: str) -> str:
    """
    Extracts the domain segment from a URL path.
    
    Example:
        /api/v1/agentverse/something -> "agentverse"
        /ws/agentverse -> "agentverse"
        /agentverse/ws -> "agentverse"
    
    Args:
        path (str): The URL path.
    
    Returns:
        str: The extracted domain segment.
    """
    logger.info(f"[🔍 WS DOMAIN] Extracting domain from path: {path}")
    parts = path.strip("/").split("/")
    # Try to find the domain segment in known positions
    if "v1" in parts:
        idx = parts.index("v1")
        if len(parts) > idx + 1:
            return parts[idx + 1]
    elif len(parts) >= 2 and parts[0] == "ws":
        return parts[1]
    elif len(parts) >= 2:
        return parts[0]
    return "unknown"