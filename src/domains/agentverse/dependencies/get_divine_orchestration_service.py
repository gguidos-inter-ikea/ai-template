from fastapi import Depends
from dependency_injector.wiring import Provide, inject
from src.base.dependencies.request_id_dependency import get_request_id
from src.domains.agentverse.dependencies.di_container import AgentverseContainer
from src.domains.agentverse.services.divine_orchestration_service import(
        DivineOrchestrationService
)

import logging

logger = logging.getLogger(__name__)

@inject
async def get_divine_orchestration_service(
        request_id: str = Depends(get_request_id),
        divine_orchestration_service: DivineOrchestrationService =
                Depends(Provide[AgentverseContainer.divine_orchestration_service])
):
    logger.info(f"creating DivnieOrchestrationService with request_id: {request_id}")
    divine_orchestration_service.request_id = request_id
    logger.info(f"DivnieOrchestrationService created {divine_orchestration_service}")
    return divine_orchestration_service