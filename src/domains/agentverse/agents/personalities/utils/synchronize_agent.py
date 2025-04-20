from src.domains.agentverse.agents.base import BaseAgent
from src.domains.agentverse.registries import agent_registry_instance
from src.domains.agentverse.logging.logger import log_evangelion_bay

def synchronize_agent(agent_blueprint: dict) -> BaseAgent:
    log_evangelion_bay("[🧠 SYNCHRONIZATION] Establishing neural sync with EVA blueprint...")
    agent_class = agent_registry_instance.get(agent_blueprint["type"])
    log_evangelion_bay("[🔗 SYNCHRONIZATION] Neural pattern successfully synchronized")
    return agent_class(**agent_blueprint)