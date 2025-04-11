from fastapi import Depends
from dependency_injector.wiring import Provide, inject
from src.domains.writer_assistant.dependencies.di_container import WriterAssistantContainer
from src.base.dependencies.request_id_dependency import get_request_id
from src.domains.writer_assistant.services.chat_service import ChatService
import logging

logger = logging.getLogger(__name__)

@inject
async def get_chat_service(
    request_id: str = Depends(get_request_id),
    chat_service: ChatService = Depends(Provide[WriterAssistantContainer.chat_service])
) -> ChatService:
    """Create a ChatService instance with the provided request_id."""
    logger.debug(f"Creating ChatService with request_id: {request_id}")
    # Set the request_id dynamically
    chat_service.request_id = request_id
    logger.debug(f"ChatService created: {chat_service}")
    return chat_service
