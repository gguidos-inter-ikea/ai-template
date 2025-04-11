from fastapi import Request
import json
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class ChatHistoryService:
    """
    Service to manage chat history using a Redis repository.
    Each chat conversation history is stored as a Redis list with a key formatted as 'chat_history:{chat_id}'.
    """

    def __init__(
            self,
            generate_history_file: callable,
            chat_history_key_prefix: str = "chat_history:",
            max_chat_history_size=3
    ):
        """
        Initialize the ChatHistoryService.

        Args:
            redis_repo: An instance of your Redis repository (e.g., RedisRepositoryImpl).
            chat_history_key_prefix: The prefix used for chat history keys (default is "chat_history:").
        """

        self.generate_history_file = generate_history_file
        self.chat_history_key_prefix = chat_history_key_prefix
        self.max_chat_history_size = max_chat_history_size

    async def append_message(
            self, 
            request: Request,
            message: Dict
    ) -> None:
        """
        Append a new message to the chat history.

        Args:
            chat_id: The unique identifier for the chat or conversation.
            message: The chat message as a dictionary.
            max_history: Optional maximum number of messages to keep (oldest messages beyond this limit will be removed).
        """
        session_key = request.app.state.session_key
        local_key = f"{session_key}:{self.chat_history_key_prefix}"
        
        # Serialize the message to JSON
        serialized_message = json.dumps(message)
        # Append the new message to the list (using lpush to add to the head)
        await request.app.state.redis_repository.lpush(local_key, serialized_message)
        
        # If a maximum history length is defined, trim the list to keep only the most recent messages.
        if self.max_chat_history_size is not None:
            # Here, 0 to max_history - 1 keeps only the latest N messages.
            await request.app.state.redis_repository.ltrim(local_key, 0, self.max_chat_history_size - 1)

    async def get_chat_history(self,
            request: Request,
            start: int = 0, 
            end: int = -1
    ) -> List[Dict]:
        """
        Retrieve the entire chat history or a specific range for the given chat ID.
        
        Args:
            chat_id: The unique identifier for the chat or conversation.
            start: The start index for the list range (default is 0 for the most recent).
            end: The end index (default of -1 means all messages).

        Returns:
            A list of chat message dictionaries.
        """
        session_key = request.app.state.session_key
        local_key = f"{session_key}:{self.chat_history_key_prefix}"
        # Retrieve the serialized messages from Redis
        messages = await request.app.state.redis_repository.lrange(local_key, start, end)
        logger.info(f"{local_key} retrieved from Redis: {messages}")
        logger.info(f"Retrieved messages: {messages}")
        # Deserialize each message from JSON
        return [json.loads(msg) for msg in messages]
    
    async def download_history(self, chat_history: List[dict]) -> list:
        """
        Retrieves the chat history.

        Args:
            request (Request): The FastAPI request object.

        Returns:
            list: The chat history.
        """
        response = self.generate_history_file(chat_history)
        
        return response
    
    async def delete_history(self, request: Request):
        session_key = request.app.state.session_key
        local_key = f"{session_key}:{self.chat_history_key_prefix}"

        return await request.app.state.redis_repository.delete(local_key)