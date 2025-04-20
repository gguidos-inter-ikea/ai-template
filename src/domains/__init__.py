"""
Domain initialization module.
This module is responsible for initializing all domain-specific containers
and extending the base container with domain-specific dependencies.
"""
from src.base.dependencies.di_container import Container as BaseContainer
# Import domain container extensions
from src.domains.user.dependencies.di_container import extend_container as extend_with_user_domain
from src.domains.writer_assistant.dependencies.di_container import extend_container as extend_with_writer_assistant_domain
from src.domains.agentverse.dependencies.di_container import extend_container as extend_with_agentverse_domain

def initialize_domains(container: BaseContainer) -> BaseContainer:
    """
    Initialize all domain-specific containers and extend the base container.
    
    Args:
        container: The base container to extend
        
    Returns:
        The extended container with all domain-specific dependencies
    """
    # Extend the container with each domain
    container = extend_with_user_domain(container)
    container = extend_with_writer_assistant_domain(container)
    container = extend_with_agentverse_domain(container)

    # Add more domains as needed:

    # container = extend_with_another_domain(container)
    # container = extend_with_yet_another_domain(container)
    
    return container

__all__ = [
    "initialize_domains",
]