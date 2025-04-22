import asyncio
from fastapi import WebSocket
from src.base.repositories.redis_repository import RedisRepository
from typing import Dict


class SocketRedisBridgeService:
    def __init__(self, redis_repository: RedisRepository):
        self.redis_repository = redis_repository
        self.active_connections: Dict[str, WebSocket] = {}
        self.channel_tasks: Dict[str, asyncio.Task] = {}

    async def connect(self, socket_id: str, websocket: WebSocket):
        """
        Accept a WebSocket connection and register it under the given socket ID.
        """
        self.active_connections[socket_id] = websocket

    async def disconnect(self, socket_id: str):
        """
        Clean up a WebSocket and cancel its Redis subscription task.
        """
        if socket_id in self.active_connections:
            await self.active_connections[socket_id].close()
            del self.active_connections[socket_id]
        if socket_id in self.channel_tasks:
            self.channel_tasks[socket_id].cancel()
            del self.channel_tasks[socket_id]

    async def subscribe(self, channel: str, socket_id: str):
        """
        Subscribe to a Redis channel and forward messages to the WebSocket client.
        """
        async def listener():
            async for message in self.redis_repository.subscribe_channel(channel):
                ws = self.active_connections.get(socket_id)
                if ws:
                    await ws.send_text(message)

        self.channel_tasks[socket_id] = asyncio.create_task(listener())

    async def send_to_socket(self, socket_id: str, message: str):
        """
        Send a message directly to a single WebSocket.
        """
        ws = self.active_connections.get(socket_id)
        if ws:
            await ws.send_text(message)

    async def broadcast_to_all(self, message: str):
        """
        Send a message to all currently connected WebSockets.
        """
        for ws in self.active_connections.values():
            await ws.send_text(message)
