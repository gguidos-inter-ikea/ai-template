import inspect
from typing import Optional
from src.domains.agentverse.registries import tool_registry_instance as tool_registry
from src.domains.agentverse.tools.base import ToolConfig
from src.domains.agentverse.tools.base import BaseTool

class ToolFactory:
    def __init__(self, **shared_deps):
        self.deps = shared_deps

    def create(self, tool_name: str, config: Optional[ToolConfig] = None) -> BaseTool:
        cls = tool_registry.get(tool_name)
        sig = inspect.signature(cls.__init__)
        init_kwargs = {
            name: dep
            for name, dep in self.deps.items()
            if name in sig.parameters
        }
        if config:
            init_kwargs["config"] = config
        return cls(**init_kwargs)
