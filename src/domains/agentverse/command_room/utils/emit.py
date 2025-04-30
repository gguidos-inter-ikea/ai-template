from src.domains.agentverse.command_room.command_room import CommandRoomTransmitter

async def emit_log(socket_id: str, message: str, commandroom: CommandRoomTransmitter):
    payload = {
        "type": "log",
        "message": message
    }
    await commandroom.to_socket(socket_id=socket_id, message=payload)  # <-- no dumps here

async def emit_event(socket_id: str, event: str, payload: dict, commandroom: CommandRoomTransmitter):
    full_payload = {
        "type": "event",
        "event": event,
        **payload
    }
    await commandroom.to_socket(socket_id=socket_id, message=full_payload)  # <-- no dumps here

async def emit_agent_event(socket_id: str, event: str, agent_id: str, agent_name: str, payload: dict, commandroom: CommandRoomTransmitter):
    full_payload = {
        "type": "event",
        "event": event,
        "agent_id": agent_id,
        "agent_name": agent_name,
        **payload
    }
    await commandroom.to_socket(socket_id=socket_id, message=full_payload)  # <-- no dumps here
