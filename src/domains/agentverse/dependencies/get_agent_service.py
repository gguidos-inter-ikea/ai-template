from fastapi import Depends
from dependency_injector.wiring import Provide, inject
from src.base.dependencies.request_id_dependency import get_request_id
from src.domains.agentverse.dependencies.di_container import AgentverseContainer
from src.domains.agentverse.services.agent_service import AgentService

import logging

logger = logging.getLogger(__name__)

@inject
async def get_agent_service(
        request_id: str = Depends(get_request_id),
        agent_service: AgentService = Depends(Provide[AgentverseContainer.agent_service])
):
    logger.info(f"creating AgentService with request_id: {request_id}")
    agent_service.request_id = request_id
    logger.info(f"AgentService created {agent_service}")
    return agent_service