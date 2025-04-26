# src/domains/agentverse/registries/tool_registry.py
from src.domains.agentverse.registries.base import Registry
from src.domains.agentverse.registries.utils.register_registry import register_registry
from src.domains.agentverse.tools.base import BaseTool
from src.domains.agentverse.exceptions import RegistrationError

@register_registry(name="Tool Registry", icon="🧰")
class ToolRegistry(Registry[BaseTool]):
    name = "tool"
    description = "Registry for EVA tools"

    def __init__(self):
        super().__init__(name=self.name)

    def _validate_component(self, component: type) -> None:
        if not issubclass(component, BaseTool):
            raise TypeError(f"Component `{component.__name__}` must inherit from BaseTool")
        # Enforce presence of required class attrs
        for attr in ("name", "version", "parameters"):
            if not hasattr(component, attr):
                raise RegistrationError(
                    message=f"Tool `{component.__name__}` missing `{attr}` attribute",
                    details={"component": component.__name__}
                )
