import logging
from typing import Dict, Any, Optional
from src.base.repositories.rabbitmq_repository import RabbitMQRepository

logger = logging.getLogger(__name__)

class PublishMessage:
    def __init__(self, repository: RabbitMQRepository):
        self.repository = repository

    def execute(self, queue_name: str, message: Dict[str, Any], properties: Optional[Dict[str, Any]] = None) -> None:
        """
        Publish a message to a specific RabbitMQ queue.

        Args:
            queue_name (str): The name of the RabbitMQ queue.
            message (dict): The message to publish.
            properties (dict, optional): Additional RabbitMQ message properties (e.g., headers, delivery_mode).
        """
        try:
            # Validate the message
            self._validate_message(message)

            # Log the publishing attempt
            logger.info(f"Publishing message to queue '{queue_name}': {message}")

            # Use the repository to publish the message
            self.repository.publish_message(queue_name, message, properties)

            # Log success
            logger.info(f"Message successfully published to queue '{queue_name}'")
        except Exception as e:
            logger.error(f"Failed to publish message to queue '{queue_name}': {e}")
            raise

    def _validate_message(self, message: Dict[str, Any]) -> None:
        """
        Validate the message structure before publishing.

        Args:
            message (dict): The message to validate.

        Raises:
            ValueError: If the message is invalid.
        """
        if not isinstance(message, dict):
            raise ValueError("Message must be a dictionary.")
        if "event_type" not in message or "details" not in message:
            raise ValueError("Message must contain 'event_type' and 'details' fields.")