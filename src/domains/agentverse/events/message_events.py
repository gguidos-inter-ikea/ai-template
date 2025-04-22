from fastapi import WebSocket
from src.domains.agentverse.command_room.command_room import CommandRoomTransmitter
from src.base.websockets.event_router import EventRouter
from src.domains.agentverse.dependencies.get_divine_orchestration_service import (
    get_divine_orchestration_service
)

def register_message_events(
    event_router: EventRouter,
    websocket: WebSocket = None,
    socket_id: str = None,
    commandroom: CommandRoomTransmitter = None
):
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
            result = await divine_service.create_agent(
                websocket=websocket,
                event_router=event_router,
                socket_id= socket_id,
                commandroom=commandroom,
                **data
            )
            return {
                "status": "✅ EVA created",
                "agent": result
            }
        
    
    @event_router.on("stimulus.environment")
    async def handle_stimulus(data):
        # agent_name = data.get("agent_name")
        # socket_id = data.get("socket_id")

        # Your agent resolution strategy may vary
        # agent = resolve_agent_from_memory(agent_name)  # placeholder

        # if not agent:
        #     return {"error": "Agent not found"}

        # reaction = await agent.reflex_engine.process(data)

        # # Broadcast reflex to the socket
        # await commandroom.to_socket(socket_id, reaction)

        # return {"reaction": reaction}
        pass
