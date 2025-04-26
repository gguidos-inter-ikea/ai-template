# registries.py
from src.domains.agentverse.registries.agent_registry import AgentRegistry
from src.domains.agentverse.registries.personality_registry import PersonalityProfileRegistry
from src.domains.agentverse.registries.tool_registry import ToolRegistry
from src.domains.agentverse.registries.base import Registry
from typing import Dict

agent_registry_instance = AgentRegistry()
personality_registry_instance = PersonalityProfileRegistry()
tool_registry_instance = ToolRegistry()

registries: Dict[str, Registry] = {
    "agent": agent_registry_instance,
    "personality": personality_registry_instance,
    "tool": tool_registry_instance,
}

__all__ = ["agent_registry_instance", "personality_registry_instance", "tool_registry_instance", "registries"]
