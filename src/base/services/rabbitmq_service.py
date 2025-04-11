from typing import Any, Dict, Optional
from src.base.repositories.rabbitmq_repository import RabbitMQRepository
from src.base.messaging.publish_message import PublishMessage
from src.base.entities.monitoring.monitoring_event_entity import MonitoringEvent
import logging

logger = logging.getLogger(__name__)

class RabbitMQService:
    """Service layer for managing RabbitMQ."""

    def __init__(self, repository: RabbitMQRepository, request_id: Optional[str] = None):
        self.repository = repository
        self.request_id = request_id

    def publish_monitoring_event(self, queue_name: str, event_type: str, details: Dict[str, Any]) -> None:
        """Publish a monitoring event to RabbitMQ."""
        event = MonitoringEvent(event_type, details)
        publish_message = PublishMessage(self.repository)
        publish_message.execute(queue_name, event.to_dict())

    def setup_queue(self, queue_name: str) -> None:
        """Setup a RabbitMQ queue."""
        self.repository.declare_queue(queue_name)
        logger.info("Additional queues declared successfully")