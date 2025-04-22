
import logging

# AgentVerse domain-specific logger
AGENTVERSE_LOGGER = logging.getLogger("agentverse")

def log_command_room(message: str):
    """Log from the perspective of the Command Room (entry point/controller)."""
    AGENTVERSE_LOGGER.info(f"[🧭 COMMAND ROOM] {message}")

def log_operations_commander(message: str):
    """Log from the perspective of the operations handler (AgentService)."""
    AGENTVERSE_LOGGER.info(f"[🧠 OPERATIONS COMMANDER] {message}")

def log_evangelion_bay(message: str):
    """Log from the Evangelion Bay (AgentFactory)."""
    AGENTVERSE_LOGGER.info(f"[🧬 EVANGELION BAY] {message}")

def log_sync_unit(message: str):
    """Log from the Neural Sync Unit (agent sync / runtime boot)."""
    AGENTVERSE_LOGGER.info(f"[🔗 SYNC CORE] {message}")

def log_nerv_hq(message: str):
    """Log from the Registry Mind (registries and memory banks)."""
    AGENTVERSE_LOGGER.info(f"[🧠 NERV HQ] {message}")

def log_existencial_index(message: str):
    """Log from the Existencial Index (db service)."""
    AGENTVERSE_LOGGER.info(f"[🧠 EXISTENCIAL INDEX] {message}")

def log_agent_existencial_core(message: str):
    """Log from the Existencial Index (db service)."""
    AGENTVERSE_LOGGER.info(f"[🧠 EXISTENCIAL INDEX] {message}")
