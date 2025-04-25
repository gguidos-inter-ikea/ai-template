from fastapi import APIRouter, Request, Depends, status
from src.domains.agentverse.entities.agent import (
    AgentRequest,
    DBAgent,
    ChatRequest
)
from src.domains.agentverse.dependencies.get_agent_service import get_agent_service
from src.domains.agentverse.dependencies.get_db_service import get_db_service
from src.domains.agentverse.services.agent_service import AgentService
from src.domains.agentverse.services.db_service import DBService
from src.domains.agentverse.logging.logger import log_command_room
from src.domains.agentverse.entities.db import DBAgentPost
from src.domains.agentverse.exceptions import (
    BlueprintConflictError
)
import logging

logger = logging.getLogger("agentverse.interface")
router = APIRouter()
    
@router.post("/api/v1/agents", status_code=status.HTTP_201_CREATED)
async def create_agent(
    request: Request,
    agent_request: AgentRequest,
    agent_service: AgentService = Depends(get_agent_service),
    db_service: DBService = Depends(get_db_service)
):
    """Create a new Agent"""
    logger.debug(f"Task received for blueprinting EVA: {agent_request.name}")
    log_command_room(f"[🧬 STAGE 1] Deploying DNA string blueprint for EVA prototype: '{agent_request.name}'")

    # 🔬 Begin genetic synthesis
    log_command_room(f"[🧬 STAGE 2] DNA sequence generation for prototype type: '{agent_request.type}' initialized")
    agent_config = agent_service.agent_config(agent_request)
    log_command_room(f"[🧬 STAGE 2] DNA sequence generation for prototype type: '{agent_request.type}' completed")
    
    log_command_room(f"[🧬 STAGE 3] Scanning agent type registry for the existing of prototype type: '{agent_request.type}'")
    if not agent_service.check_if_agent_type_exists(agent_config.type):
        log_command_room(
            f"[🛑 ABORT] Unknown EVA prototype type: '{agent_config.type}' — DNA sequence deployment failed."
        )
        raise BlueprintConflictError(field="type", value=agent_config.type)
    log_command_room(f"[🧬 STAGE 3] Scanning agent type registry for the existing of prototype type: '{agent_request.type}' completed")
    # 🧠 Scan component resonance
    log_command_room(f"[🧬 STAGE 4] Scanning core cognitive configuration for prototype type: '{agent_request.type}'")
    agent_service.validate_component_types(request, agent_config)
    log_command_room(f"[🧬 STAGE 4] Scanning core cognitive configuration for prototype type: '{agent_request.type}' completed")
    # 🧿 Scan existing registry for name collision
    log_command_room(f"[🧬 STAGE 5] Scanning existing EVA DNA string index for name collision for EVA: '{agent_request.name}'")
    await db_service.check_for_duplicates(request, agent_config)
    log_command_room(f"[🧬 STAGE 5] Scanning existing EVA DNA string index for name collision for EVA: '{agent_request.name}' completed"
                     )
    # 🛠️ Assembly protocol
    log_command_room(f"[🧬 STAGE 6] DNA string assembly for EVA: '{agent_request.name}'")
    agent = agent_service.create_agent(agent_config)

    db_agent = DBAgent(
        user_id=agent_request.user_id,
        agent=agent
    )
    log_command_room(f"[🧬 STAGE 6] DNA string assembly for EVA: '{agent_request.name}' completed")
    logger.debug(f"EVA prototype '{agent_request.name}' successfully encoded.")
    log_command_room(f"[✅ STAGE COMPLETE] DNA string blueprint for EVA '{agent_request.name}' successfully deployed.")
    
    # 📦 Final storage
    inserted_agent = await db_service.store_agent(request, db_agent)
    return inserted_agent

@router.get("/api/v1/agents")
async def find_all_agents(
    request: Request,
    db_service: DBService = Depends(get_db_service)
):
    
    results = await db_service.find_all(request)

    return results

@router.post("/api/v1/agents/chat/{id}")
async def chat_with_agent(
    id: str,
    request: Request,
    chat_request: ChatRequest,
    db_service: DBService = Depends(get_db_service),
    agent_service: AgentService = Depends(get_agent_service)
):
    log_command_room(f"[🕶️ INIT] Activation directive received for prototype '{id}' — sequence authorized.")
    
    agent_data = await db_service.find_chat_agent(request, id)

    db_agent = DBAgentPost(**agent_data)
    
    log_command_room(f"[🔎 DNA] Retrieval of genetic memory core for '{id}' — confirmed.")
    
    log_command_room("[⚙️ SYNC] Cognitive matrix reconstruction initiated.")
    built_agent = await agent_service.build_agent(request=request, db_agent=db_agent)

    log_command_room(f"[🌌 DIV-OPS] '{id}' synchronized. Soul-link established. Operational awareness initiated.")
    
    log_command_room("[🎯 EXEC] Operational phase initiated — task payload loading...")
    response = agent_service.execute_task(message=chat_request.message, agent=built_agent)
    
    log_command_room(f"[✔️ EXEC] Task execution completed — prototype '{id}' stable.")
    
    return response

