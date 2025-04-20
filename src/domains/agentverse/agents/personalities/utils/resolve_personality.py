from src.domains.agentverse.registries import personality_registry_instance
from src.domains.agentverse.entities.agent import AgentConfig
from src.domains.agentverse.entities.agent_soul_protocol import AgentSoulProtocol
from src.domains.agentverse.logging.logger import log_evangelion_bay


def resolve_personality(agent_config: AgentConfig) -> AgentSoulProtocol:
    log_evangelion_bay(f"[🧬 PERSONALITY RESOLUTION] Resolving personality for EVA '{agent_config.personality_profile}'...")

    # Priority 1: Full custom personality passed directly
    if agent_config.personality:
        log_evangelion_bay("[🧠 PERSONALITY LOAD] Custom EVA personality traits detected — overriding registry reference.")
        return agent_config.personality

    # Priority 2: Named reference to a known personality profile
    if agent_config.personality_profile:
        try:
            profile_class = personality_registry_instance.get(agent_config.personality_profile)
            log_evangelion_bay(f"[🧬 PROFILE BINDING] Retrieved '{agent_config.personality_profile}' from Personality Registry.")
            return profile_class()
        except KeyError:
            log_evangelion_bay(f"[❌ PROFILE MISSING] Unknown profile '{agent_config.personality_profile}' — fallback to Generic EVA.")

    # Priority 3: Fallback to Mortal EVA
    try:
        fallback = personality_registry_instance.get("Mortal EVA")
        log_evangelion_bay("[🌑 NO TRAITS FOUND] No profile provided — defaulting to 'Mortal EVA'.")
        return fallback()
    except KeyError:
        log_evangelion_bay("[💀 CRITICAL] Fallback profile 'Mortal EVA' not found in Personality Registry.")
        raise RuntimeError("EVA personality resolution failed — 'Mortal EVA' profile is missing.")
