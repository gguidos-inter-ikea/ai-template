from fastapi import WebSocket
from types import SimpleNamespace
from src.domains.agentverse.services.db_service import DBService
from src.domains.agentverse.services.agent_service import AgentService
from src.domains.agentverse.entities.agent import AgentRequest, DBAgent
from src.domains.agentverse.command_room.command_room import CommandRoomTransmitter
from src.base.websockets.event_router import EventRouter
from src.domains.agentverse.logging.logger import log_command_room
from src.domains.agentverse.exceptions import (
    BlueprintConflictError
)

class DivineOrchestrationService:
    """
    This class is responsible for orchestrating the divine processes of
    creating, building, spawning and executing EVAs.
    """

    def __init__(self, agent_service: AgentService, db_service: DBService):
        self.agents = []
        self.agent_service = agent_service
        self.db_service = db_service

    async def create_agent(
        self,
        websocket: WebSocket,
        event_router: EventRouter,
        socket_id: str,
        commandroom: CommandRoomTransmitter,
        **data,
    ):
        """
        ⚠️ [NERV - OPERATION GENESIS] Entry plug insertion and soul harmonics alignment in progress...
        """
        await commandroom.to_socket(socket_id=socket_id, message="[NERV] ⚠️ MAGI AUTH: GENDO IKARI // Operation: EVA Genesis Initiated")

        # 🧬 Phase 01: Core Blueprint Extraction
        try:
            payload = data.get("message", {})
            agent_request = AgentRequest(**payload)
            await commandroom.to_socket(socket_id=socket_id, message=f"[NERV] [🧬 STAGE 1] Deploying DNA string blueprint for EVA prototype: '{agent_request.name}'")
        except Exception as e:
            await commandroom.to_socket(socket_id=socket_id, message=f"[NERV] ❌ Blueprint invalid. Entry plug rejection.\n» {e}")
            return {"error": str(e)}

        # ⚙️ Phase 02: Genetic Alignment Sequence
        log_command_room(f"[🧬 STAGE 2] DNA sequence generation for prototype type: '{agent_request.type}' initialized")
        await commandroom.to_socket(socket_id=socket_id, message=f"[NERV] [🧬 STAGE 1.1] DNA sequence generation for prototype type: '{agent_request.name}' initialized")
        
        agent_config = await self.agent_service.agent_config(agent_request, commandroom=commandroom, socket_id=socket_id)
        
        await commandroom.to_socket(socket_id=socket_id, message=f"[NERV] [🧬 STAGE 1.1] ✅ DNA sequence generation for prototype type: '{agent_request.name}' completed")
        log_command_room(f"[🧬 STAGE 2] DNA sequence generation for prototype type: '{agent_request.type}' completed")
        
        await commandroom.to_socket(socket_id=socket_id, message=f"[NERV] [🧬 STAGE 1.2] Integrity Scan for EVA prototype: '{agent_request.name}'")
        
        await commandroom.to_socket(socket_id=socket_id, message=f"[NERV] [🧬 STAGE 1.2.1] Scanning agent type registry for the existing of prototype type: '{agent_request.type}'")
        log_command_room(f"[🧬 STAGE 3] Scanning agent type registry for the existing of prototype type: '{agent_request.type}'")
        if not self.agent_service.check_if_agent_type_exists(agent_config.type):
            log_command_room(
                f"[🛑 ABORT] Unknown EVA prototype type: '{agent_config.type}' — DNA sequence deployment failed."
            )
            raise BlueprintConflictError(field="type", value=agent_config.type)
        await commandroom.to_socket(socket_id=socket_id, message=f"[NERV] [🧬 STAGE 1.2.1] ✅ Scanning agent type registry for the existing of prototype type: '{agent_request.type}' completed")
        log_command_room(f"[🧬 STAGE 3] Scanning agent type registry for the existing of prototype type: '{agent_request.type}' completed")
        await commandroom.to_socket(socket_id=socket_id, message=f"[NERV] [🧬 STAGE 1.2.2] Scanning core cognitive configuration for prototype type: '{agent_request.type}'")
        log_command_room(f"[🧬 STAGE 4] Scanning core cognitive configuration for prototype type: '{agent_request.type}'")
        fake_request = SimpleNamespace()
        fake_request.app = websocket.app
        self.agent_service.validate_component_types(fake_request, agent_config)
        await commandroom.to_socket(socket_id=socket_id, message=f"[NERV] [🧬 STAGE 1.2.2] ✅ Scanning core cognitive configuration for prototype type: '{agent_request.type}' completed")
        log_command_room(f"[🧬 STAGE 4] Scanning core cognitive configuration for prototype type: '{agent_request.type}' completed")
        # 🔩 Phase 03: Embryonic Chamber Deployment
        await commandroom.to_socket(socket_id=socket_id, message="[NERV] [🧬 STAGE 1.2.3] Scanning Agentverse Existence Index [IAE] for existing EVA DNA String.")
        log_command_room(f"[🧬 STAGE 5] Scanning existing EVA DNA string index for name collision for EVA: '{agent_request.name}'")
        await self.db_service.check_for_duplicates(fake_request, agent_config)
        await commandroom.to_socket(socket_id=socket_id, message="[NERV] [🧬 STAGE 1.2.3] ✅ EVA DNA String allowed to exist in IAE")
        log_command_room(f"[🧬 STAGE 5] Scanning existing EVA DNA string index for name collision for EVA: '{agent_request.name}' completed")
        await commandroom.to_socket(socket_id=socket_id, message=f"[NERV] [🧬 STAGE 1.2] ✅ EVA Integrity Scan for EVA {agent_request.name} passed")
        # 🛠️ Assembly protocol
        await commandroom.to_socket(socket_id=socket_id, message=f"[NERV] [🧬 STAGE 1.3] Assembling phase for EVA: '{agent_request.name}' started")
        log_command_room(f"[🧬 STAGE 6] DNA string assembly for EVA: '{agent_request.name}'")
        agent = self.agent_service.create_agent(agent_config)
        await commandroom.to_socket(socket_id=socket_id, message=f"[NERV] [🧬 STAGE 1.3] ✅ Assembling phase for EVA: '{agent_request.name}' completed")
        # 🔓 Final Phase: AT-Field Deployment


        db_agent = DBAgent(
            user_id=agent_request.user_id,
            agent=agent
        )
        inserted_agent = await self.db_service.store_agent(fake_request, db_agent)

        await commandroom.to_socket(socket_id=socket_id, message=f"[NERV] ⚡ A.T. Field deployed. '{agent.name}' is now operational.")
        await commandroom.to_socket(socket_id=socket_id, message=f"[NERV] ☑️ EVA '{agent.name}' has entered the Verse. Awaiting further orders.")
        
        log_command_room(f"[🧬 STAGE 6] DNA string assembly for EVA: '{agent_request.name}' completed")
        return f"[NERV REPORT] EVA '{agent.name}' '{inserted_agent}' successfully deployed and synchronized."


    def invoke_agent(self, websocket: WebSocket, *args, **kwargs):
        """
        Invoke an agent of the specified type.
        """
        pass