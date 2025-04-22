from dependency_injector import containers, providers

from src.base.dependencies.containers import (
    DatabaseContainer,
    OpenAIContainer,
    MonitorContainer,
    ServiceContainer,
    RedisContainer,
    RateLimiterContainer,
    MessagingContainer,
    SettingsContainer,
    ChromaDBContainer,
    SocketContainer
)

class DomainsHolder:
    pass
class Container(containers.DeclarativeContainer):
    """
    Root container that merges all domain-specific containers.
    """
    # Sub-containers
    wiring_config = containers.WiringConfiguration(
        modules=[
            "src.base.dependencies.rate_limiter_dependencies",
            "src.base.dependencies.jwt_dependencies",
            "src.base.config.config"
        ],
        auto_wire=True
    )
    database = providers.Container(DatabaseContainer)
    openai = providers.Container(OpenAIContainer)
    monitoring = providers.Container(MonitorContainer)
    services = providers.Container(ServiceContainer)
    redis = providers.Container(RedisContainer)
    rate_limiter = providers.Container(RateLimiterContainer)
    messaging = providers.Container(MessagingContainer)
    settings_container = providers.Container(SettingsContainer)
    chromadb = providers.Container(ChromaDBContainer)
    socket = providers.Container(SocketContainer)
    
    domains = providers.Object(DomainsHolder())


# Create a container instance for the application
container = Container()


