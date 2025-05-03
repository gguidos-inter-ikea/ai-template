from typing import Optional, Dict, Any, Callable
from pydantic import BaseModel
from src.domains.agentverse.entities.agent_soul_protocol_parts.agent_soul_protocol import AgentSoulProtocol

class PersonalityFactory:
    def __init__(self, get_personality_class: Callable):
        self.get_personality_class = get_personality_class

    def create_base(self, name: str, description: str, prompt: Optional[str] = None) -> AgentSoulProtocol:
        """
        Create a minimal base personality with only name, description, and prompt.
        The prompt is stored as a keyword in the expression_profile.
        """
        return AgentSoulProtocol(
            identity_profile={"name": name, "description": description},
            expression_profile={"vocal_expression_keywords": [prompt] if prompt else []}
        )

    def create_from_archetype(
        self, archetype: str, overrides: Optional[Dict[str, Any]] = None
    ) -> AgentSoulProtocol:
        """
        Load a predefined archetype from the registry and apply optional overrides.
        """
        personality_class = self.get_personality_class(archetype)
        base = personality_class().model_copy(deep=True)
        if overrides:
            base = base.model_copy(update=overrides)
        return base

    def create_partial_soul(self, **profiles: BaseModel) -> AgentSoulProtocol:
        """
        Build a soul from only the specified profile parts.
        Missing parts will fall back to default values.
        """
        soul = AgentSoulProtocol()
        for key, value in profiles.items():
            if hasattr(soul, key):
                setattr(soul, key, value)
        return soul

    def enrich(
        self, base: AgentSoulProtocol, updates: Optional[Dict[str, BaseModel]] = None
    ) -> AgentSoulProtocol:
        """
        Merge a base personality with additional or updated profiles.
        """
        if updates:
            for key, value in updates.items():
                if hasattr(base, key):
                    setattr(base, key, value)
        return base

    def add_custom_traits(self, personality: AgentSoulProtocol, traits: Dict[str, Any]) -> AgentSoulProtocol:
        """
        Adds or overrides custom traits at any depth of the personality.
        Supports flat or nested field access.
        """
        for key, value in traits.items():
            if hasattr(personality, key):
                setattr(personality, key, value)
            else:
                for profile_name in personality.model_fields:
                    profile = getattr(personality, profile_name, None)
                    if profile and isinstance(profile, BaseModel) and hasattr(profile, key):
                        setattr(profile, key, value)
                        break
                else:
                    setattr(personality, key, value)
        return personality
