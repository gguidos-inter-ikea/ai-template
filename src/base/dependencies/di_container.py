from dependency_injector import containers, providers
from dependency_injector.containers import DynamicContainer

from src.base.dependencies.containers import (
    DatabaseContainer,
    OpenAIContainer,
    MonitorContainer,
    ServiceContainer,
    RedisContainer,
    RateLimiterContainer,
    MessagingContainer,
    SettingsContainer
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

    # Use a single dynamic container to hold all domains.
    # Instead of a DynamicContainer, use a plain holder.
    domains = providers.Object(DomainsHolder())


# Create a container instance for the application
container = Container()


