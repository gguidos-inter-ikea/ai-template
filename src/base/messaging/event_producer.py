from typing import Dict, Any
from src.base.services.event_filtering_service import EventFilteringService
from src.base.messaging.event_publisher import EventPublisher
from src.base.entities.monitoring.event_factory import EventFactory
import logging

logger = logging.getLogger(__name__)

class EventProducer:
    """Producer for orchestrating event filtering and publishing."""

    def __init__(self,
                 filtering_service: EventFilteringService,
                 event_publisher: EventPublisher,
                 event_factory: EventFactory):
        self.filtering_service = filtering_service
        self.event_publisher = event_publisher
        self.event_factory = event_factory

    def produce_event(self, event_type: str, details: Dict[str, Any]) -> None:
        """
        Orchestrate the filtering and publishing of an event.

        Args:
            event_type (str): The type of the event (e.g., "error", "security").
            details (dict): Additional details about the event.
        """
        try:
            # Check if the event should be created
            if not self.filtering_service.should_create_event(event_type, details):
                logger.info(f"Event of type '{event_type}' filtered out.")
                return

            # Create the event object
            event = self.event_factory.create_event(event_type=event_type, details=details)

            # Publish the event
            self.event_publisher.publish(event)
        except Exception as e:
            logger.error(f"Failed to process event of type '{event_type}': {e}")
            raise