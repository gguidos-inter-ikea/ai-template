import logging
from dependency_injector import containers, providers
from src.base.monitors.event_monitor.event_monitor import EventMonitor
from src.base.monitors.event_monitor.event_registry import EventRegistry
from src.base.config.config import settings

logger = logging.getLogger(__name__)

class MonitorContainer(containers.DeclarativeContainer):
    """
    Container for monitoring-related dependencies.
    """
    # Dynamically load all registered event handlers
    full_dispatch_map = EventRegistry.get_registered_handlers()

    # Filter dispatch map based on observable_log_types
    dispatch_map = {
        event_type: handler
        for event_type, handler in full_dispatch_map.items()
        if event_type.split("_")[0] in settings.monitoring.observable_log_types
    }

    # Log a warning for unmapped event types
    unmapped_events = [
        event_type for event_type in full_dispatch_map
        if event_type.split("_")[0] not in settings.monitoring.observable_log_types
    ]
    if unmapped_events:
        logger.warning(f"The following events are not mapped\
                       to observable log types: {unmapped_events}")

    # EventMonitor singleton
    event_monitor = providers.Singleton(
        EventMonitor,
        log_paths=settings.monitoring.observable_log_paths,
        dispatch_map=dispatch_map,
    )