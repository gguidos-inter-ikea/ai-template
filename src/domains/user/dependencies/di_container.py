"""
Domain-specific dependency injection container that extends the base container.
"""
from dependency_injector import containers, providers
from src.base.dependencies.di_container import Container as BaseContainer
from src.domains.user.repositories.user_repository import UserRepository
from src.domains.user.services.user_service import UserService

class UserContainer(containers.DeclarativeContainer):
    """
    Container for the User domain that extends the base container.
    """
    # Enable auto-wiring for better compatibility with FastAPI's
    # dependency injection
    wiring_config = containers.WiringConfiguration(
        modules=[
            "src.domains.user.dependencies.get_user_service",
            "src.domains.user.interfaces.api.v1.controller",
        ],
        auto_wire=True
    )
    
    # Import the base container for use in this container
    base = providers.Container(BaseContainer)
    
    # Domain-specific repositories
    user_repository = providers.Singleton(
        UserRepository,
        client=base.database.mongo_client
    )
    
    # Domain-specific services
    user_service = providers.Singleton(
        UserService,
        repository=user_repository
    )

def extend_container(base_container: BaseContainer) -> BaseContainer:
    user_container = UserContainer()# <-- safe override here

    user_container.wire(modules=[
        "src.domains.user.dependencies.get_user_service",
        "src.domains.user.interfaces.api.v1.controller",
    ])

    base_container.user_repository = user_container.user_repository
    base_container.user_service = user_container.user_service

    return base_container
    
    