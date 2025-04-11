from pydantic_settings import BaseSettings

class MessagingConfig(BaseSettings):
    """
    RabbitMQ and messaging-related settings.
    """
    rabbitmq_host: str = "localhost"
    rabbitmq_port: int = 5672
    rabbitmq_user: str = "guest"
    rabbitmq_password: str = "guest"
    rabbitmq_heartbeat: int = 600
    rabbitmq_monitoring_queue: str = "monitoring"
    rabbitmq_monitoring_enabled: bool = True