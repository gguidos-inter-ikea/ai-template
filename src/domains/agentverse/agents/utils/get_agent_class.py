
def get_agent_class(agent_type: str):
    """
    Get the agent class based on the agent type.
    """
    from src.domains.agentverse.registries.registries import agent_registry_instance
    return agent_registry_instance.get(agent_type)