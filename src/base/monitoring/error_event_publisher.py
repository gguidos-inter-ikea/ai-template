import logging
from src.base.messaging.publish_message import PublishMessage

logger = logging.getLogger(__name__)

class ErrorEventPublisher:
    def __init__(self, publish_message: PublishMessage, queue_name: str):
        """
        Initialize the ErrorEventPublisher.

        Args:
            publish_message (PublishMessage): The PublishMessage instance for publishing messages.
            queue_name (str): The RabbitMQ queue name for error events.
        """
        self.publish_message = publish_message
        self.queue_name = queue_name

    def publish_error_event(self, error_type: str, details: dict):
        """
        Publish an error event to the RabbitMQ queue.

        Args:
            error_type (str): The type of the error (e.g., "application_error", "database_error").
            details (dict): Additional details about the error.
        """
        event = {
            "event_type": "error",
            "error_type": error_type,
            "details": details,
        }
        try:
            self.publish_message.execute(self.queue_name, event)
            logger.info(f"Published error event: {event}")
        except Exception as e:
            logger.error(f"Failed to publish error event: {e}")