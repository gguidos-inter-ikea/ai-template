import logging

logger = logging.getLogger(__name__)
def safe_get_agent_class(agent_type: str):
    from src.domains.agentverse.registries.registries import agent_registry_instance
    return agent_registry_instance.get(agent_type)


def safe_get_personality_class(personality_type: str):
    from src.domains.agentverse.registries.registries import personality_registry_instance
    logger.info(personality_type)
    return personality_registry_instance.get(personality_type)