from fastapi import APIRouter, Request, Depends, status
from src.domains.agentverse.entities.agent import (
    AgentRequest,
    DBAgent,
    ChatRequest
)
from src.domains.agentverse.dependencies.get_agent_service import get_agent_service
from src.domains.agentverse.dependencies.get_db_service import get_db_service
from src.domains.agentverse.dependencies.get_registry_service import get_registry_service
from src.domains.agentverse.services.agent_service import AgentService
from src.domains.agentverse.services.registry_service import RegistryService
from src.domains.agentverse.services.db_service import DBService
from src.domains.agentverse.logging.logger import log_command_room
from src.domains.agentverse.entities.db import DBAgentPost
from src.domains.agentverse.services.personality_service import PersonalityService
from src.domains.agentverse.dependencies.get_personality_service import get_personality_service
from src.domains.agentverse.entities.agent_soul_protocol_parts.agent_soul_protocol import AgentSoulProtocol
from src.domains.agentverse.exceptions import (
    BlueprintConflictError
)
import logging

logger = logging.getLogger("agentverse.interface")
router = APIRouter()

def diff_dump(soul: AgentSoulProtocol) -> dict:
    baseline = AgentSoulProtocol()                       # canonical defaults
    raw      = soul.model_dump(exclude_none=True)        # full object, minus None
    base     = baseline.model_dump(exclude_none=True)
    return {k: v for k, v in raw.items() if v != base.get(k)}

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

@router.get("/api/v1/agents/list")
async def find_all_agents(
    request: Request,
    db_service: DBService = Depends(get_db_service)
):
    results = await db_service.find_all(request)
    return results

@router.get("/api/v1/agents/id/{agent_id}")
async def find_agent(
    agent_id: str,
    request: Request,
    db_service: DBService = Depends(get_db_service)
):  
    results = await db_service.find_chat_agent(request, agent_id)
    return results


@router.get("/api/v1/agents/personalities/{name}/soul")
async def get_soul(
    name: str,
    personality_service: PersonalityService = Depends(get_personality_service)
):
    soul = personality_service.extract_soul(name)
    return soul.minimal_dump()

@router.get("/api/v1/agents/cognitive-modules/keys")
async def list_cognitive_module_keys(request: Request):
    cm       = request.app.state.cognitive_modules
    defaults = request.app.state.cognitive_defaults

    return {
        category: {
          "options": list(backends.keys()),
          "default": defaults[category]
        }
        for category, backends in cm.items()
    }

@router.get("/api/v1/agents/soul-protocol/schema", tags=["agents"])
def get_agent_soul_protocol_schema():
    # Return the full nested model with default values
    return AgentSoulProtocol().model_json_schema()

@router.get("/api/v1/agents/cognitive-modules/llm")
def list_llm(request: Request):
    return list(request.app.state.cognitive_modules["llm"].keys())

@router.get("/api/v1/agents/registry/{type}")
async def get_agent_types(
    type: str,
    registry_service: RegistryService = Depends(get_registry_service)
):
    
    results = registry_service.list(type, include_metadata=True)

    return results

@router.get("/api/v1/agents/registries/{registry_type}/entry/{entry_name}")
async def get_registry_entry_details(
    registry_type: str,
    entry_name: str,
    registry_service: RegistryService = Depends(get_registry_service),
):
    """Retrieve full details of a specific registry entry."""
    try:
        # Instead of get_registry(), use get_component() like your service defines
        component_cls = registry_service.get_component(registry_type, entry_name)
        component_instance = component_cls()
        return component_instance.model_dump()
    
    except ValueError as ve:
        return {"error": str(ve)}
    except KeyError:
        return {"error": f"Entry '{entry_name}' not found in registry '{registry_type}'."}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}

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

