from typing import Optional
from src.domains.agentverse.entities.agent_soul_protocol import AgentSoulProtocol
from src.domains.agentverse.registries import personality_registry_instance


@personality_registry_instance.register(name="Empty EVA", description="Empty EVA Prototype")
class EmptyEVA(AgentSoulProtocol):
    name: str = "empty_eva"
    description: Optional[str] = "An EVA prototype with no traits."