from fastapi import APIRouter, Request, Depends
from src.base.decorators.middleware.session_based import session_based
from src.domains.writer_assistant.entities.metadata import RequestData
from src.domains.writer_assistant.services.chat_service import ChatService
from src.domains.writer_assistant.services.chat_history_service import ChatHistoryService
from src.domains.writer_assistant.dependencies.get_chat_history_service import (
    get_chat_history_service
)
from src.domains.writer_assistant.dependencies.get_chat_service import get_chat_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/api/v1/writer_assistant/send")
@session_based
async def send_message(
    request: Request,
    messageRequest: RequestData,
    chat_service: ChatService = Depends(get_chat_service),
    chat_history_service: ChatHistoryService = Depends(get_chat_history_service)
):
    logger.info("send_message endpoint called")
    
    # Get the JSON body from the request as a dictiona
    
    # Do additional processing as needed
    chat_history = await chat_history_service.get_chat_history(
        request
    )

    response = await chat_service.send_message(
        request,
        messageRequest,
        chat_history
    )
    
    return response

@router.get("/api/v1/writer_assistant/download_history")
@session_based
async def download_history(
    request: Request,
    chat_history_service: ChatHistoryService = Depends(get_chat_history_service)
):
    logger.info("download_history endpoint called")
    
    # Do additional processing as needed
    chat_history = await chat_history_service.get_chat_history(request)
    response = await chat_history_service.download_history(
        request,
        chat_history
    )
    
    return response

@router.delete("/api/v1/writer_assistant/delete_history")
@session_based
async def delete_history(
    request,
    chat_history_service: ChatHistoryService = Depends(get_chat_history_service)
):
    return await chat_history_service.delete_history(request)