from typing import Type
from src.domains.agentverse.entities.agent_soul_protocol import AgentSoulProtocol
from src.domains.agentverse.registries.base import Registry
from src.domains.agentverse.registries.utils.register_registry import register_registry
from src.domains.agentverse.logging.logger import log_nerv_hq

@register_registry(name="Personality Registry", icon="💫")
class PersonalityProfileRegistry(Registry[AgentSoulProtocol]):
    """
    Specialized Registry for managing predefined EVA Personality Archetypes.

    This registry handles the classification, retrieval, and instantiation of
    personality blueprints used to imbue EVA agents with psychological depth.
    """

    name = "personality_registry"
    description = "Registry for EVA personality archetypes"
    version = "1.0.0"

    def __init__(self):
        super().__init__(name=self.name)

    def _validate_component(self, component: Type[AgentSoulProtocol]) -> None:
        if not issubclass(component, AgentSoulProtocol):
            raise TypeError("Only subclasses of PersonalityProfile are allowed.")
        log_nerv_hq(f"[🧠 VALIDATION] PersonalityProfile '{component.__name__}' passed schema integrity check.")
