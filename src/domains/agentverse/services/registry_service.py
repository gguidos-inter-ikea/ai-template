
from typing import Dict, Any, Optional, List, Type
from src.domains.agentverse.registries.base import Registry, RegistryItem

class RegistryService:
    """
    A façade over our various NERV-HQ registries (agent, personality, tool).
    """

    def __init__(self, registries: Dict[str, Registry[Any]]):
        # e.g. {"agent":agent_registry, "tool":tool_registry, ...}
        self._registries = registries

    def _get_registry(self, which: str) -> Registry[Any]:
        try:
            return self._registries[which]
        except KeyError:
            raise ValueError(f"Registry '{which}' not found")

    def list(
        self,
        which: str,
        include_metadata: bool = False
    ) -> List[Any]:
        """
        List either the names or full metadata for a given registry.
        """
        reg = self._get_registry(which)
        return reg.list(include_metadata=include_metadata)

    def get_info(
        self,
        which: str,
        name: str
    ) -> Optional[RegistryItem]:
        """
        Get the RegistryItem for a single component.
        """
        reg = self._get_registry(which)
        info = reg.get_info(name)
        if info is None:
            raise KeyError(f"Component '{name}' not found in registry '{which}'")
        return info

    def get_component(
        self,
        which: str,
        name: str,
        version: Optional[str] = None
    ) -> Type[Any]:
        """
        Retrieve the actual class (agent, tool, personality, etc.).
        """
        reg = self._get_registry(which)
        return reg.get(name, version)

    def get_metrics(self, which: str) -> Dict[str, Any]:
        """
        Pull performance/usage metrics from a registry.
        """
        reg = self._get_registry(which)
        return reg.get_metrics()
