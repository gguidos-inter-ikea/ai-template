from fastapi import Request
from typing import List
from src.domains.writer_assistant.entities.metadata import Metadata, RequestData
from src.domains.writer_assistant.handlers.chat_handler import ChatHandler
import logging

logger = logging.getLogger(__name__)

class ChatService:
    """
    Service class for handling chat interactions with the OpenAI API.
    """

    def __init__(
            self,
            chat_handler: ChatHandler,
            generate_prompts: callable
        ):
        """
        Initialize the ChatService.

        Args:
            chat_history_service (ChatHistoryService): Service for managing chat history.
        """
        self.chat_handler = chat_handler
        self.generate_prompts = generate_prompts

    async def send_message(self, request: Request, messageRequest: RequestData, chat_history: List[dict]) -> str:
        """
        Sends a message to the OpenAI API and returns the response.

        Args:
            metadata (Metadata): Metadata object containing chat details.

        Returns:
            str: The response from the OpenAI API.
        """
        metadata = self.generate_metadata(messageRequest)
        prompt_text = metadata.prompt_text

        # Generate the prompt based on the metadata
        default_system_prompt, content_prompt = self.generate_prompts(metadata)

        # Calculate the maximum tokens based on the maximum character length
        max_tokens = self.chat_handler.max_tokens(metadata.max_char_length)
        model = request.app.state.settings.ai_models.model
        response = await self.chat_handler.send_prompt_to_llm(
            request,
            default_system_prompt,
            content_prompt,
            max_tokens,
            chat_history,
            model
        )

        history_message = {
            "prompt": prompt_text,
            "generated_text": response,
            "char_length": len(response)
        }

        self.chat_history_service.add_message(request, history_message)
        return response[0]
    
    def generate_metadata(self, messageRequest: RequestData) -> Metadata:
        return Metadata(
            role=messageRequest.role,
            style=messageRequest.style,
            mood=messageRequest.mood,
            audience=messageRequest.audience,
            prompt_text=messageRequest.prompt_text,
            feedback=messageRequest.feedback,
            ikea_rules=messageRequest.ikea_rules,
            ikea_style=messageRequest.ikea_style,
            max_char_length=messageRequest.max_char_length,
            min_words=messageRequest.min_words,
            max_words=messageRequest.max_words,
            min_sentences=messageRequest.min_sentences,
            max_sentences=messageRequest.max_sentences
        )