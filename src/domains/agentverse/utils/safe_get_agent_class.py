def safe_get_agent_class(agent_type: str):
    from src.domains.agentverse.registries.registries import agent_registry_instance
    return agent_registry_instance.get(agent_type)