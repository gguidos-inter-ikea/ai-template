import logging
from src.base.messaging.publish_message import PublishMessage
from src.base.config.config import Settings
from src.base.entities.monitoring.event_entities import Event

logger = logging.getLogger(__name__)

class EventPublisher:
    def __init__(
            self,
            publish_message: PublishMessage,
            settings: Settings
        ):
        self.publish_message = publish_message
        self.event_configurations =\
            settings.event_config.get_configuration()

    def publish(self, event: Event) -> None:
        """
        Publish an event to the appropriate RabbitMQ queue.

        Args:
            event (Event): The event to publish.
        """
        event_type = event.event_type

        try:
            # Access the configuration for the event type
            config = self.event_configurations[event_type]
            queue_name = config["queue_name"]

            # Publish the event
            self.publish_message.execute(queue_name, event.to_dict())
            logger.info(f"Published {event_type} event: {event.to_dict()}")

        except KeyError:
            logger.error(f"No configuration found for event type '{event_type}'")
        except Exception as e:
            logger.error(f"Failed to publish {event_type} event: {e}")