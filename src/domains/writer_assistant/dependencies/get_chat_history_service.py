from fastapi import Depends
from dependency_injector.wiring import Provide, inject
from src.domains.writer_assistant.dependencies.di_container import WriterAssistantContainer
from src.base.dependencies.request_id_dependency import get_request_id
from src.domains.writer_assistant.services.chat_history_service import ChatHistoryService
import logging

logger = logging.getLogger(__name__)

@inject
async def get_chat_history_service(
    request_id: str = Depends(get_request_id),
    chat_history_service: ChatHistoryService = Depends(Provide[WriterAssistantContainer.chat_history_service])
) -> ChatHistoryService:
    """Create a ChatHistoryService instance with the provided request_id."""
    logger.debug(f"Creating ChatHistoryService with request_id: {request_id}")
    # Set the request_id dynamically
    chat_history_service.request_id = request_id
    logger.debug(f"ChatHistoryService created: {chat_history_service}")
    return chat_history_service