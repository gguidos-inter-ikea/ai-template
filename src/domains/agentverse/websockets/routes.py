from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from src.base.decorators.middleware.ws_session_based import session_based_ws
from src.domains.agentverse.decorators.commander_only_ws import commander_only_ws
from src.domains.agentverse.command_room.command_room import CommandRoomTransmitter
from src.domains.agentverse.events.message_events import register_message_events
from src.domains.agentverse.exceptions import handle_ws_exception
import asyncio
from uuid import uuid4
import logging
import json
router = APIRouter()
logger = logging.getLogger("agentverse.interface")
connected_clients = set()

async def onboarding_sequence(websocket: WebSocket, session_key: str):
    await websocket.send_text(json.dumps({"type": "log", "message": "[💠 Joshu-A][Socket Broadcast Center] Existence detected..."}))
    await asyncio.sleep(0.1)
    await websocket.send_text(json.dumps({"type": "log", "message": "[💠 Joshu-A][Socket Broadcast Center] ⭓ Scanning DNA signature for permission..."}))
    await asyncio.sleep(0.1)
    await websocket.send_text(json.dumps({"type": "log", "message": "[💠 Joshu-A][Socket Broadcast Center] ⭓ Protocol alignment: ✓"}))
    await asyncio.sleep(0.1)
    await websocket.send_text(json.dumps({"type": "log", "message": "[💠 Joshu-A][Socket Broadcast Center] ⭓ Archetype match: In Progress..."}))
    await asyncio.sleep(0.1)
    await websocket.send_text(json.dumps({"type": "log", "message": "[💠 Joshu-A][Socket Broadcast Center] ✅ Access granted. Welcome, Soulform."}))
    await asyncio.sleep(0.1)
    await websocket.send_text(json.dumps({"type": "log", "message": f"[💠 Joshu-A][Socket Broadcast Center] 𒀭 𒂗 𒆠 :: Temp memory assigned key: {session_key}"}))
    await asyncio.sleep(0.1)
    await websocket.send_text(json.dumps({"type": "log", "message": "[💠 Joshu-A][Socket Broadcast Center] 𒀭 𒂗 𒆠 :: COMM PROTOCOL ESTABLISHED"}))
    await asyncio.sleep(0.1)
    await websocket.send_text(json.dumps({"type": "log", "message": "[💠 Joshu-A][Socket Broadcast Center] 𒀭 𒂗 𒆠 :: UTU SECURITY PROTOCOL EMBEDDED"}))




@router.websocket("/ws/api/v1/Joshu-A")
@session_based_ws(on_ready=onboarding_sequence)
@commander_only_ws
async def ws_handler(websocket: WebSocket):
    connected_clients.add(websocket)
    event_router = websocket.app.state.event_router
    socket_id = str(uuid4())
    session_key = websocket.scope.get("session_key", "unknown")
    agent_name = websocket.query_params.get("agent")

    commbridge = websocket.app.state.cognitive_modules["communication"]["socketRedisBridge"]
    commandroom = CommandRoomTransmitter(commbridge)
    await commbridge.connect(socket_id, websocket)

    register_message_events(
        websocket=websocket,
        event_router=event_router,
        socket_id=socket_id,
        commandroom=commandroom
    )

    if agent_name:
        await commbridge.subscribe(f"agent:{agent_name.lower()}", socket_id)

    try:
        while True:
            message = await websocket.receive_json()
            event = message.get("event")
            data = message.get("data", {})

            handler = event_router.get(event)
            if handler:
                try:
                    response = await handler(data)
                    if response is not None:
                        await websocket.send_json({"event": event, "response": response})
                except Exception as e:
                    error_response = await handle_ws_exception(commandroom, socket_id, e)
                    await websocket.send_json({"event": event, "error": error_response})
            else:
                await websocket.send_json({"error": f"No handler for event '{event}'"})

    except WebSocketDisconnect:
        await commbridge.disconnect(socket_id)
        connected_clients.remove(websocket)


@router.websocket("/ws/api/v1/agent/{agent_system_name}")
@session_based_ws(on_ready=onboarding_sequence)
async def ws_chat_handler(websocket: WebSocket, agent_system_name: str):
    connected_clients.add(websocket)
    event_router = websocket.app.state.event_router
    socket_id = str(uuid4())
    session_key = websocket.scope.get("session_key", "unknown")
    
    # 🔄 Access cognitive modules
    commbridge = websocket.app.state.cognitive_modules["communication"]["socketRedisBridge"]
    commandroom = CommandRoomTransmitter(commbridge)

    # ✅ Receive first message to extract agent info
    first_message = await websocket.receive_json()
    event = first_message.get("event", "").lower()
    data = first_message.get("data", {})

    agent_system_name = first_message.get("agent_system_name") or event.split(".")[0]
    agent_system_name = agent_system_name.lower()
    agent_id = first_message.get("agent_id", None)

    # 🌟 FIRST: Register handlers based on agent name
    register_message_events(
        event_router=event_router,
        websocket=websocket,
        socket_id=socket_id,
        agent_system_name=agent_system_name,
        agent_id=agent_id,
        commandroom=commandroom
    )

    handler = event_router.get(event)

    # ✅ Dispatch first event properly
    if handler:
        response = await handler(data)
        await websocket.send_json({"event": event, "response": response})
    else:
        await websocket.send_json({"error": f"No handler for event '{event}'"})

    # 🔁 Start main message loop
    try:
        while True:
            msg = await websocket.receive_json()
            msg_event = msg.get("event", "").lower()
            msg_data = msg.get("data", {})
            agent_id = msg.get("agent_id", None)
            agent_system_name = msg.get("agent_system_name") or msg_event.split(".")[0]  # ✅ fixed here

            handler = event_router.get(msg_event)

            if handler:
                try:
                    response = await handler(msg_data)
                    await websocket.send_json({"event": msg_event, "response": response})
                except Exception as e:
                    logger.exception(f"❌ Handler for event '{msg_event}' failed")
                    await websocket.send_json({"event": msg_event, "error": str(e)})
            else:
                await websocket.send_json({"error": f"No handler for event '{msg_event}'"})

    except WebSocketDisconnect:
        await commbridge.disconnect(socket_id)
        connected_clients.remove(websocket)
