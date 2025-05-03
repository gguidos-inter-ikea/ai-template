from typing import Optional
from src.domains.agentverse.entities.agent_soul_protocol import AgentSoulProtocol
class EmptyEVA(AgentSoulProtocol):
    name: str = "empty_eva"
    description: Optional[str] = "An EVA prototype with no traits."