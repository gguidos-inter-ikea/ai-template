# utils.py
from src.domains.agentverse.registries.registries import registries
from src.domains.agentverse.registries.base import Registry
import logging

logger = logging.getLogger(__name__)

def get_registry(name: str) -> Registry:
    if name not in registries:
        raise KeyError(f"Registry '{name}' not found")
    logger.debug(f"Retrieved registry: {name}")
    return registries[name]

def reset_registries() -> None:
    for name, registry in registries.items():
        if hasattr(registry, "reset"):
            registry.reset()
            logger.info(f"Reset registry: {name}")
        else:
            logger.warning(f"Registry '{name}' does not implement reset")

__all__ = ["get_registry", "reset_registries"]
