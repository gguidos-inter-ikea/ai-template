from src.domains.agentverse.agents.base import BaseAgent
from src.domains.agentverse.registries.base import Registry
from src.domains.agentverse.registries.utils.register_registry import register_registry

import logging

logger = logging.getLogger(__name__)

@register_registry(name="Agent Registry", icon="🧠")
class AgentRegistry(Registry[BaseAgent]):
    name = "Agent registry"
    description = "Registry for agent classes"

    def __init__(self):
        super().__init__(name=self.name)

    def _validate_component(self, component):
        if not issubclass(component, BaseAgent):
            raise TypeError("Registered agent must inherit from BaseAgent")
