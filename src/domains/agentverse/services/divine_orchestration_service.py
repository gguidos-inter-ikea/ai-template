from fastapi import WebSocket
import traceback
from types import SimpleNamespace
from src.domains.agentverse.services.db_service import DBService
from src.domains.agentverse.services.agent_service import AgentService
from src.domains.agentverse.entities.agent import AgentRequest, DBAgent
from src.domains.agentverse.command_room.command_room import CommandRoomTransmitter
from src.domains.agentverse.logging.logger import log_command_room
from src.domains.agentverse.agents.utils.get_or_spawn_agent import get_or_spawn_agent
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
        log_command_room(f"[🧬 STAGE 1.1] DNA sequence generation for prototype type: '{agent_request.type}' initialized")
        await commandroom.to_socket(socket_id=socket_id, message=f"[NERV] [🧬 STAGE 1.1] DNA sequence generation for prototype: '{agent_request.name}' initialized")

        agent_config = await self.agent_service.agent_config(agent_request, commandroom=commandroom, socket_id=socket_id)

        await commandroom.to_socket(socket_id=socket_id, message=f"[NERV] [🧬 STAGE 1.1] ✅ DNA sequence generation for '{agent_request.name}' completed")
        log_command_room("[🧬 STAGE 1.1] DNA sequence generation completed")

        await commandroom.to_socket(socket_id=socket_id, message=f"[NERV] [🧬 STAGE 1.2] Integrity Scan for EVA: '{agent_request.name}'")
        fake_request = SimpleNamespace()
        fake_request.app = websocket.app

        # Type validation
        if not self.agent_service.check_if_agent_type_exists(agent_config.type):
            error_msg = f"[🛑 ABORT] Unknown EVA prototype type: '{agent_config.type}' — DNA sequence deployment failed."
            log_command_room(error_msg)
            raise BlueprintConflictError(field="type", value=agent_config.type)

        await commandroom.to_socket(socket_id=socket_id, message=f"[NERV] ✅ EVA type '{agent_request.type}' is valid.")
        await commandroom.to_socket(socket_id=socket_id, message="[NERV] [🧬 STAGE 1.2.2] Validating component configuration...")

        self.agent_service.validate_component_types(fake_request, agent_config)
        await commandroom.to_socket(socket_id=socket_id, message="[NERV] ✅ Component configuration valid.")

        # Duplicate check
        await commandroom.to_socket(socket_id=socket_id, message=f"[NERV] Checking IAE for existing EVA with name: '{agent_request.name}'...")
        await self.db_service.check_for_duplicates(fake_request, agent_config)
        await commandroom.to_socket(socket_id=socket_id, message=f"[NERV] ✅ EVA '{agent_request.name}' DNA string cleared by Agentverse Existence Index.")

        # 🛠️ Phase 03: Assembly
        await commandroom.to_socket(socket_id=socket_id, message=f"[NERV] [🧬 STAGE 1.3] Assembling EVA '{agent_request.name}'...")
        agent = self.agent_service.create_agent(agent_config)
        await commandroom.to_socket(socket_id=socket_id, message=f"[NERV] ✅ EVA '{agent.name}' assembled.")

        db_agent = DBAgent(user_id=agent_request.user_id, agent=agent)
        inserted_agent_id = await self.db_service.store_agent(fake_request, db_agent)

        # Try both approaches safely

        
        await commandroom.to_socket(socket_id=socket_id, message=f"[NERV] ✅ EVA '{inserted_agent_id}' DNA string stored in the Agentverse Existence Index.")
        if not inserted_agent_id:
            raise ValueError("Could not retrieve '_id' from inserted_agent")

        spawned_agent = await get_or_spawn_agent(
            request=fake_request,
            agent_id=inserted_agent_id,
            db_service=self.db_service,
            agent_service=self.agent_service,
            cache=websocket.app.state.cognitive_modules["cache"]["redis"],
            agent_registry=getattr(self, "active_agents", None)
)
        await self.self_test_and_sleep(spawned_agent, commandroom, socket_id)

        await commandroom.to_socket(socket_id=socket_id, message=f"[NERV] ⚡ A.T. Field deployed. '{spawned_agent.name}' is now operational.")
        await commandroom.to_socket(socket_id=socket_id, message=f"[NERV] ☑️ EVA '{spawned_agent.name}' has entered the Verse. Awaiting further orders.")

        log_command_room(f"[🧬 COMPLETE] EVA '{spawned_agent.name}' fully deployed, tested, and archived.")
        return f"[NERV REPORT] EVA '{spawned_agent.name}' '{inserted_agent_id}' successfully deployed and synchronized."



    async def chat_w_agent(
        self,
        websocket: WebSocket,
        socket_id: str,
        agent_id: str,
        agent_system_name: str,
        commandroom: CommandRoomTransmitter,
        **data
    ):
        """
        Chat with an EVA agent via websocket and CommandRoom.
        """
        try:
            payload = data.get("message", {})
            if not agent_id:
                error_msg = "[NERV] ❌ No agent_id provided for EVA lookup."
                await commandroom.to_socket(socket_id=socket_id, message=error_msg)
                return {"error": error_msg}

            await commandroom.to_socket(
                socket_id=socket_id,
                message=f"[NERV] [🧬 STAGE 1] Checking EVA memory for '{agent_system_name}' (ID: {agent_id})"
            )

            fake_request = SimpleNamespace()
            fake_request.app = websocket.app

            # 🧠 Retrieve or build agent
            agent = await get_or_spawn_agent(
                request=fake_request,
                agent_id=agent_id,
                db_service=self.db_service,
                agent_service=self.agent_service,
                cache=websocket.app.state.cognitive_modules["cache"]["redis"],
                agent_registry=getattr(self, "active_agents", None)
            )

            # 🧬 Process the message
            response = await self.agent_service.execute_task(message=payload, agent=agent)
            
            await commandroom.to_socket(
                socket_id=socket_id,
                message={
                    "department": "[DOS][NERV] [🧬 STAGE 2] EVA response received.",
                    "status": "✅ EVA replied",
                    "response": response
                }
            )
            return {"response": response}

        except Exception as e:
            await commandroom.to_socket(
                socket_id=socket_id,
                message=f"[NERV] ❌ Blueprint invalid. Entry plug rejection.\n» {e}"
            )
            return {"error": str(e)}


    async def self_test_and_sleep(self, agent, commandroom, socket_id: str):
        """
        [🧪 POST-CREATION SELF TEST]
        Verifies the EVA agent's cognitive loop by sending a test message and logging the response,
        before placing the agent into a dormant state.
        """
        try:
            # 🗣️ Send test signal
            await commandroom.to_socket(socket_id, f"[DOS] [🧪 SELF TEST] Sending neural ping to EVA '{agent.system_name}'...")
            test_message = "This is Joshu-A. Can you hear me?"
            await commandroom.to_socket(socket_id, f"[DOS] [🧪 SELF TEST] This is Joshu-A contacting EVA '{agent.system_name}'. Can you hear me?")
            # 🧬 Process the message
            response = await self.agent_service.execute_task(message=test_message, agent=agent)
            
            # 🔍 Normalize response for logging
            if isinstance(response, dict):
                response_text = response.get("message") or response.get("text") or str(response)
            else:
                response_text = str(response)

            # Ensure it's a clean string
            safe_response = str(response)
            await agent.remember("first_response", safe_response)


            # 📘 Log and remember the first response
            await commandroom.to_socket(socket_id, f"[DOS] ✅ EVA '{agent.system_name}' responded: {response_text}")
            await agent.remember("first_response", response_text)

            # 💤 Sleep the agent (mark as not spawned)
            await commandroom.to_socket(socket_id, f"[DOS] 💤 EVA '{agent.system_name}' now entering dormant mode.")
            await agent.sleep()

            return {
                "status": "success",
                "message": f"EVA '{agent.system_name}' successfully self-tested and deactivated."
            }

        except Exception as e:
            error_trace = traceback.format_exc()
            await commandroom.to_socket(socket_id, f"[DOS] ❌ Self test failed for EVA '{agent.system_name}': {str(e)}\n{error_trace}")
            return {"status": "error", "message": str(e)}
