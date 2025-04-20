from functools import wraps
from src.domains.agentverse.logging.logger import log_nerv_hq


def register_registry(name: str, icon: str = "📘"):
    """
    Decorator to register and log the initialization of a Registry class.
    """
    def decorator(cls):
        original_init = cls.__init__

        @wraps(original_init)
        def wrapped_init(self, *args, **kwargs):
            log_nerv_hq(f"[{icon} REGISTRY] Initializing registry '{name}'...")
            original_init(self, *args, **kwargs)
            self.name = name
            if hasattr(self, "get_metrics"):
                self.get_metrics()
            log_nerv_hq(f"[{icon} READY] Registry '{name}' successfully initialized.")
        
        cls.__init__ = wrapped_init
        return cls

    return decorator