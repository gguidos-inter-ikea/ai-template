from dependency_injector import containers, providers
from src.base.dependencies.di_container import Container as BaseContainer
from src.domains.agentverse.utils.safe_get_agent_class import safe_get_agent_class
from src.domains.agentverse.agents.utils.get_agent_class import get_agent_class
from src.domains.agentverse.utils.generate_dna_sequence import (
    generate_dna_sequence
)
from src.domains.agentverse.agents.personalities.utils.synchronize_agent import (
    synchronize_agent
)
from src.domains.agentverse.agents.personalities.utils.resolve_personality import (
    resolve_personality
)
from src.domains.agentverse.agents.factory import (
    AgentFactory
)
from src.domains.agentverse.services.agent_service import (
    AgentService
)
from src.domains.agentverse.services.db_service import (
    DBService
)
from src.domains.agentverse.services.divine_orchestration_service import (
    DivineOrchestrationService
)

class AgentverseContainer(containers.DeclarativeContainer):
    """
    Dependency injection container for the Writer Assistant domain.
    """

    db_service = providers.Factory(
        DBService
    )

    agent_factory = providers.Factory(
        AgentFactory,
        resolve_personality = resolve_personality,
        synchronize_agent = synchronize_agent,
        generate_dna_sequence = generate_dna_sequence,
        get_agent_class = get_agent_class
        
    )

    agent_service = providers.Factory(
        AgentService,
        agent_factory = agent_factory,
        safe_get_agent_class = safe_get_agent_class
    )

    divine_orchestration_service = providers.Factory(
        DivineOrchestrationService,
        agent_service = agent_service,
        db_service = db_service
    )

def extend_container(base_container: BaseContainer) -> BaseContainer:
    agentverse_container = AgentverseContainer()# <-- safe override here

    agentverse_container.wire(modules=[
        "src.domains.agentverse.dependencies.get_db_service",
        "src.domains.agentverse.dependencies.get_agent_service",
        "src.domains.agentverse.interfaces.api.v1.interface",
        "src.domains.agentverse.dependencies.get_divine_orchestration_service",
        "src.domains.agentverse.services.divine_orchestration_service",
    ])

    base_container.agent_service = agentverse_container.agent_service

    return base_container