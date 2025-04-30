from fastapi import WebSocket
from typing import Optional
from src.domains.agentverse.command_room.command_room import CommandRoomTransmitter
from src.base.websockets.event_router import EventRouter
from src.domains.agentverse.dependencies.get_divine_orchestration_service import (
    get_divine_orchestration_service
)
import json
import logging

logger = logging.getLogger("agentverse.interface")

def register_message_events(
    event_router: EventRouter,
    websocket: WebSocket = None,
    socket_id: str = None,
    agent_system_name: Optional[str] = None,
    agent_id: Optional[str] = None,
    commandroom: CommandRoomTransmitter = None
):
    # 🛰️ Always register static Joshu-A handlers
    @event_router.on("joshu-a.comm")
    async def handle_send_message(data):
        return {
            "status": "🛰️ Joshu-A: Do you want to play a game?",
            "received": data.get("text", "")
        }

    if websocket and commandroom:
        @event_router.on("joshu-a.create")
        async def handle_create_message(data):
            divine_service = await get_divine_orchestration_service()
            await divine_service.create_agent(
                websocket=websocket,
                event_router=event_router,
                socket_id=socket_id,
                commandroom=commandroom,
                **data
            )

    # 💬 Skip dynamic agent handler if name is missing
    if not agent_system_name:
        logger.warning("[⚠️ register_message_events] agent_name is None — skipping dynamic agent handler")
        return

    agent_name = agent_system_name.lower()
    event_id = f"{agent_system_name}.comm"
    logger.info(f"[🧠 Registering handler for]: {event_id}")

    if websocket and commandroom and event_id not in event_router.handlers:
        @event_router.on(event_id)
        async def handle_agent_comm(data: dict):
            logger.debug(f"📩 {agent_name} received: {data}")
            await commandroom.to_socket(socket_id, agent_id)
            try:
                divine_service = await get_divine_orchestration_service()
                result = await divine_service.chat_w_agent(
                    websocket=websocket,
                    event_router=event_router,
                    socket_id=socket_id,
                    agent_id=agent_id,
                    agent_system_name=agent_name,
                    commandroom=commandroom,
                    **data
                )
                from datetime import datetime
                def serialize_datetime(obj):
                    if isinstance(obj, datetime):
                        return obj.isoformat()
                    return obj

                clean_response = json.loads(json.dumps(result, default=serialize_datetime))
                await commandroom.to_socket(socket_id, clean_response)
                return {"status": "✅ Message sent", "message": clean_response}
            except Exception as e:
                logger.exception("❌ Error handling agent message")
                await commandroom.to_socket(socket_id, {"error": str(e)})
                return {"status": "❌ Failed", "error": str(e)}

    @event_router.on("stimulus.environment")
    async def handle_stimulus(data):
        pass

    logger.info(f"[🧠 All registered handlers] {list(event_router.handlers.keys())}")
