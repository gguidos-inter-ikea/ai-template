from typing import Dict, Any, Type, Optional, ClassVar, List, TypeVar, Generic, Callable
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

from src.domains.agentverse.logging.logger import log_nerv_hq
from src.domains.agentverse.exceptions import RegistrationError

T = TypeVar("T")

class RegistryItem(BaseModel):
    """Metadata structure for a registered component."""
    name: str
    description: Optional[str] = None
    version: str = "1.0.0"
    metadata: Dict[str, Any] = Field(default_factory=dict)
    registration_time: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(extra="allow")

class Registry(Generic[T]):
    """
    NERV-HQ Themed Registry System for the AgentVerse.

    Manages registration, instantiation, and metrics for EVA-compatible components.
    """

    name: ClassVar[str] = "base_registry"
    description: ClassVar[str] = "Base component registry"
    version: ClassVar[str] = "1.1.0"

    def __init__(self, name: str, validate_components: bool = True, track_metrics: bool = True):
        self._name = name
        self._registry: Dict[str, Type[T]] = {}
        self._items: Dict[str, RegistryItem] = {}
        self.validate_components = validate_components
        self.track_metrics = track_metrics
        self.registration_count = 0
        log_nerv_hq(f"[⚙️ SYSTEM ONLINE] Registry '{self._name}' v{self.version} initialized.")

    def register(
        self,
        name: str,
        description: Optional[str] = None,
        version: str = "1.0.0",
        metadata: Optional[Dict[str, Any]] = None,
        component: Optional[Type[T]] = None,
    ) -> Callable[[Type[T]], Type[T]]:
        def decorator(comp: Type[T]) -> Type[T]:
            try:
                if self.validate_components:
                    self._validate_component(comp)

                if name in self._registry:
                    log_nerv_hq(f"[⚠️ OVERRIDE] Overwriting existing component: '{name}'")

                self._registry[name] = comp
                self._items[name] = RegistryItem(
                    name=name,
                    description=description or comp.__doc__,
                    version=version,
                    metadata=metadata or {},
                )
                self.registration_count += 1

                log_nerv_hq(f"[🧠 REGISTERED] '{name}' v{version} committed to registry '{self._name}'")
                return comp

            except Exception as e:
                log_nerv_hq(f"[🚨 REGISTRATION FAILURE] Component '{name}' rejected: {e}")
                raise RegistrationError(
                    message=f"Failed to register component '{name}': {str(e)}",
                    details={
                        "name": name,
                        "version": version,
                        "type": comp.__name__,
                    },
                )

        return decorator(component) if component else decorator

    def get(self, name: str, version: Optional[str] = None) -> Type[T]:
        if name not in self._registry:
            log_nerv_hq(f"[❌ LOOKUP FAILURE] Requested component '{name}' not found in registry '{self._name}'")
            raise KeyError(f"Component '{name}' not found in {self._name} registry")

        component = self._registry[name]
        if version and self._items[name].version != version:
            log_nerv_hq(f"[❌ VERSION MISMATCH] '{name}' version '{version}' not available — found: {self._items[name].version}")
            raise KeyError(f"Component '{name}' version {version} not found (found {self._items[name].version})")

        log_nerv_hq(f"[🧠 RETRIEVAL] Accessed component '{name}' from registry '{self._name}'")
        return component

    def build(self, name: str, **kwargs) -> T:
        component_class = self.get(name)
        log_nerv_hq(f"[🏗️ ASSEMBLY] Instantiating '{name}' from registry '{self._name}'")
        return component_class(**kwargs)

    def list(self, include_metadata: bool = False) -> List[Any]:
        if include_metadata:
            component_list = [
                {
                    "name": name,
                    "description": getattr(self._registry[name], "__doc__", ""),
                    **item.model_dump()
                }
                for name, item in self._items.items()
            ]
            log_nerv_hq(
                f"[📡 QUERY] Registry '{self._name}' metadata listing requested — "
                f"{len(component_list)} components with full intel."
            )
            return component_list

        component_names = list(self._registry.keys())
        log_nerv_hq(
            f"[📡 QUERY] Registry '{self._name}' listing requested — "
            f"{len(component_names)} components available: {component_names}"
        )
        return component_names


    def get_info(self, name: str) -> Optional[RegistryItem]:
        return self._items.get(name)

    def get_metrics(self) -> Dict[str, Any]:
        metrics = {
            "name": self._name,
            "version": self.version,
            "component_count": len(self),
            "registered_types": self.list(),
            "status": "active" if len(self) else "empty",
        }
        log_nerv_hq(f"[📊 METRICS] Registry '{self._name}': {metrics}")
        return metrics

    def unregister(self, name: str) -> None:
        self._registry.pop(name, None)
        self._items.pop(name, None)
        log_nerv_hq(f"[🗑️ UNREGISTERED] Component '{name}' purged from registry '{self._name}'")

    def reset(self) -> None:
        self._registry.clear()
        self._items.clear()
        self.registration_count = 0
        log_nerv_hq(f"[♻️ RESET] Registry '{self._name}' reset to empty state")

    def _validate_component(self, component: Type[T]) -> None:
        pass  # You can extend this in subclass

    def __contains__(self, name: str) -> bool:
        return name in self._registry

    def __len__(self) -> int:
        return len(self._registry)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self._name}', components={len(self)})"
