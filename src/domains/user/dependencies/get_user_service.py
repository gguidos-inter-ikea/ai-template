from fastapi import Depends
from dependency_injector.wiring import Provide, inject
from src.domains.user.services.user_service import UserService
from src.domains.user.dependencies.di_container import UserContainer
from src.base.dependencies.request_id_dependency import get_request_id
import logging
logger = logging.getLogger(__name__)

@inject
async def get_user_service(
    request_id: str = Depends(get_request_id),  # First, get the request ID
    user_service: UserService = Depends(Provide[UserContainer.user_service])
) -> UserService:
    """Create a UserService instance with the provided request_id."""
    logger.debug(f"Creating UserService with request_id: {request_id}")
    # Create a UserService instance and set the request_id dynamically.
    user_service.request_id = request_id
    logger.debug(f"UserService created: {user_service}")
    return user_service