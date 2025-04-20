from typing import Callable
from fastapi import Request
from src.domains.agentverse.agents.factory import (
    AgentFactory
)
from src.domains.agentverse.entities.agent import (
    AgentConfig,
    AgentRequest
)
from src.domains.agentverse.entities.db import (
    DBAgentPost
)
from src.domains.agentverse.logging.logger import log_operations_commander
from src.domains.agentverse.exceptions import (
    UnknownAgentTypeError,
    InvalidComponentError
)
import logging

logger = logging.getLogger(__name__)

class AgentService:
    def __init__(
            self,
            agent_factory: AgentFactory,
            safe_get_agent_class: Callable
    ):
        self.agent_factory = agent_factory
        self.safe_get_agent_class = safe_get_agent_class

    def check_if_agent_type_exists(self, agent_type: str) -> bool:
        try:
            log_operations_commander(f"[🔬 ANALYSIS] Scanning prototype type: '{agent_type}'")
            self.safe_get_agent_class(agent_type)
            log_operations_commander(f"[✅ VERIFIED] Type '{agent_type}' is registered and active")
            log_operations_commander(f"[🔬 ANALYSIS] Scanning prototype type: '{agent_type}'")
            return True
        except KeyError:
            log_operations_commander(f"[🛑 ABORT] Unknown EVA prototype type: '{agent_type}' – resonance failed.")
            raise UnknownAgentTypeError(value=agent_type)

    def validate_component_types(self, request: Request, config: AgentConfig):
        modules = request.app.state.cognitive_modules
        errors = []
        log_operations_commander(f"[🔬 EVA VALIDATION] Initiating resonance scan for core cognitive configuration: '{config.name}'")
        # llm_type must always be validated, even if None
        if not config.llm_type or config.llm_type not in modules.get("llm", {}):
            errors.append(("llm_type", config.llm_type))

        # Optional checks for non-null values
        if config.db_type and config.db_type not in modules.get("db", {}):
            errors.append(("db_type", config.db_type))
        if config.cache_type and config.cache_type not in modules.get("cache", {}):
            errors.append(("cache_type", config.cache_type))
        if config.knowledge_db_type and config.knowledge_db_type not in modules.get("knowledge_db", {}):
            errors.append(("knowledge_db_type", config.knowledge_db_type))

        if errors:
            for f, v in errors:
                log_operations_commander(
                    f"[❌ CORE MISMATCH] '{f}'='{v}' does not align with the required spiritual frequency. EVA assembly aborted."
                )

            raise InvalidComponentError(errors)
    
        log_operations_commander(
            "[✅ SYNCHRONIZATION STABLE] Core configuration passed resonance scan — cognitive core alignment successful."
        )

    
    def agent_config(self, agent_request: AgentRequest):
        log_operations_commander(f"[🔬 EVA ASSEMBLY] Sequencing DNA for prototype type '{agent_request.type}'")
        agent_config = AgentConfig(
            user_id = agent_request.user_id,
            name=agent_request.name,
            type=agent_request.type,
            prompt=agent_request.prompt,
            llm_type=agent_request.llm_type,
            db_type=agent_request.db_type,
            cache_type=agent_request.cache_type,
            knowledge_db_type=agent_request.knowledge_db_type,
            personality_profile=agent_request.personality_profile,
            personality=agent_request.personality,
            messaging_type=agent_request.messaging_type

        )
        log_operations_commander(f"[🔬 EVA ASSEMBLY] Sequencing DNA for prototype type '{agent_request.type}' completed")
        return agent_config

    def create_agent(self, agent_config: AgentConfig):
        logger.debug(f"Task received for blueprinting: {agent_config.name}")
        log_operations_commander(f"[🔬 EVA ASSEMBLY] Blueprinting { agent_config.name }")
        agent = self.agent_factory.create_agent(agent_config)
        logger.debug(f"[Completed] Blueprinting { agent_config.name } finished")
        log_operations_commander(f"[🔬 EVA ASSEMBLY] Blueprinting { agent_config.name } completed")
        return agent
    
    def build_agent(self, request, db_agent: DBAgentPost) -> DBAgentPost:
        agent = self.agent_factory.build_agent(request, db_agent)
        log_operations_commander(f"[🔧 EVA CONSTRUCTION] Building EVA '{agent.name}'")
        if agent is None:
            raise RuntimeError("Agent construction failed — factory returned None.")
        return agent
    
    def execute_task(self, message, agent):
        if agent is None:
            raise RuntimeError("Agent construction failed — factory returned None.")
        
        return agent.respond(message)