from functools import wraps
from fastapi import WebSocket
import logging

logger = logging.getLogger("agentverse.commander_only_ws")
def commander_only_ws(func):
    @wraps(func)
    async def wrapper(websocket: WebSocket, *args, **kwargs):
        if not websocket.scope.get("commander", False):
            await websocket.send_text("[🛑 Joshu-A] Access denied. Commander privilege required.")
            await websocket.close(code=4003)
            return
        return await func(websocket, *args, **kwargs)
    return wrapper