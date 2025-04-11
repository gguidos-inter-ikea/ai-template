from dependency_injector import containers, providers
from src.base.infrastructure.messaging.rabbitMQ.pika_client import PikaClient
from src.base.repositories.rabbitmq_repository import RabbitMQRepository
from src.base.services.rabbitmq_service import RabbitMQService
from src.base.messaging.publish_message import PublishMessage
from src.base.messaging.event_producer import EventProducer
from src.base.services.event_filtering_service import EventFilteringService
from src.base.messaging.create_consumer import ConsumeQueue
from src.base.entities.monitoring.event_factory import EventFactory
from src.base.messaging.event_publisher import EventPublisher
from src.base.config.config import settings

class MessagingContainer(containers.DeclarativeContainer):
    """IoC container for messaging components."""

    # RabbitMQ client
    pika_client = providers.Singleton(
        PikaClient,
        host=settings.messaging.rabbitmq_host
    )

    # RabbitMQ repository
    rabbitmq_repository = providers.Factory(
        RabbitMQRepository,
        pika_client=pika_client,
    )

    # RabbitMQ service
    rabbitmq_service = providers.Factory(
        RabbitMQService,
        repository=rabbitmq_repository,
    )

    # Publish
    publish = providers.Factory(
        PublishMessage,
        repository=rabbitmq_repository,  # Use RabbitMQRepository
    )

    # Event publisher
    publisher = providers.Factory(
        EventPublisher,
        publish_message=publish,
        settings=settings
    )

    event_factory = providers.Factory(
        EventFactory
    )

    filtering_service = providers.Singleton(
        EventFilteringService,
        settings=settings
    )

    # Event producer
    producer = providers.Factory(
        EventProducer,
        filtering_service=filtering_service,
        event_publisher=publisher,
        event_factory=event_factory,
    )

    # Queue consumer
    consumer = providers.Factory(
        ConsumeQueue,
        repository=rabbitmq_repository
    )