from typing import Optional, Dict, Any, Callable
from src.domains.agentverse.entities.agent import AgentConfig
from src.domains.agentverse.entities.agent_soul_protocol import AgentSoulProtocol
from src.domains.agentverse.personalities.personality_factory import PersonalityFactory
from src.domains.agentverse.logging.logger import log_evangelion_bay
from src.domains.agentverse.registries import personality_registry_instance
import logging

logger = logging.getLogger(__name__)

def deep_trim(raw: Dict[str, Any], base: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively drop keys whose value is identical to the baseline."""
    out = {}
    for k, v in raw.items():
        if k not in base:                           # new key – keep it
            out[k] = v
        else:
            b = base[k]
            if isinstance(v, dict) and isinstance(b, dict):
                trimmed = deep_trim(v, b)
                if trimmed:                        # keep only if something left
                    out[k] = trimmed
            elif v != b:                          # primitive and different
                out[k] = v
    return out


def diff_dump(soul: AgentSoulProtocol) -> Dict[str, Any]:
    baseline = AgentSoulProtocol()
    raw  = soul.model_dump(exclude_none=True)
    base = baseline.model_dump(exclude_none=True)
    return deep_trim(raw, base)

class PersonalityService:
    def __init__(self, personality_factory: PersonalityFactory, get_personality_class: Callable):
        self.personality_factory = personality_factory
        self.get_personality_class = get_personality_class

    def resolve(self, config: AgentConfig) -> AgentSoulProtocol:
        log_evangelion_bay(f"[🧬 PERSONALITY RESOLUTION] Resolving personality for EVA '{config.name}'")

        if config.personality:
            log_evangelion_bay("[🧠 PERSONALITY LOAD] Custom EVA personality traits detected — overriding archetype.")
            return config.personality
        if config.personality_profile:
            try:
                return self.personality_factory.create_from_archetype(config.personality_profile)
            except Exception as e:
                log_evangelion_bay(f"[❌ PROFILE MISSING] Unknown profile '{config.personality_profile}' — fallback engaged: {e}")

        log_evangelion_bay("[🌑 NO TRAITS FOUND] No profile provided — defaulting to base personality.")
        return self.personality_factory.create_base_personality()

    def create_base(self, name: str, description: str, prompt: Optional[str] = None) -> AgentSoulProtocol:
        return self.personality_factory.create_base(name, description, prompt)

    def create_base_personality(self) -> AgentSoulProtocol:
        return self.personality_factory.create_base_personality()

    def create_from_archetype(self, archetype: str, overrides: Optional[Dict[str, Any]] = None) -> AgentSoulProtocol:
        return self.personality_factory.create_from_archetype(archetype, overrides)

    def create_partial_soul(self, **profiles: Any) -> AgentSoulProtocol:
        return self.personality_factory.create_partial_soul(**profiles)

    def enrich(self, base: AgentSoulProtocol, updates: Optional[Dict[str, Any]] = None) -> AgentSoulProtocol:
        return self.personality_factory.enrich(base, updates)

    def add_custom_traits(self, personality: AgentSoulProtocol, traits: Dict[str, Any]) -> AgentSoulProtocol:
        return self.personality_factory.add_custom_traits(personality, traits)
    
    def extract_soul(self, name: str) -> Dict[str, Any]:
        logger.info(name)
        cls = personality_registry_instance.get(name)   # lookup
        return cls()   

