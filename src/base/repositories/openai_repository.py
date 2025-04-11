from typing import Dict, List
import logging
from src.base.infrastructure.ai.openai_client import OpenAIClient  # Your OpenAIClient implementation

logger = logging.getLogger(__name__)

class OpenAIRepository:
    """
    Repository that implements OpenAIClient operations.
    This class acts as an abstraction layer so your application
    can use OpenAI API functionality without directly coupling to the client.
    """

    def __init__(self, openai_client: OpenAIClient):
        """
        Initialize the repository with an instance of OpenAIClient.

        Args:
            openai_client: An instance of OpenAIClient (with sync and async methods).
        """
        self.client = openai_client

    def get_embeddings(self, text: str) -> List[float]:
        """
        Synchronously retrieve the embedding vector for the given text.

        Args:
            text (str): The input text for which to retrieve embeddings.
            
        Returns:
            List[float]: The embedding vector.
        """
        try:
            return self.client.get_embeddings(text)
        except Exception as e:
            logger.error(f"Error retrieving embeddings: {e}")
            raise

    async def get_embeddings_async(self, text: str) -> List[float]:
        """
        Asynchronously retrieve the embedding vector for the given text.

        Args:
            text (str): The input text for which to retrieve embeddings.
            
        Returns:
            List[float]: The embedding vector.
        """
        try:
            return await self.client.get_embeddings_async(text)
        except Exception as e:
            logger.error(f"Error retrieving embeddings asynchronously: {e}")
            raise

    def get_completion(self, prompt: str, max_tokens: int = 150) -> str:
        """
        Synchronously get a text completion for the given prompt.

        Args:
            prompt (str): The prompt to send to the API.
            max_tokens (int): Maximum number of tokens to generate.
            
        Returns:
            str: The generated text completion.
        """
        try:
            return self.client.get_completion(prompt, max_tokens)
        except Exception as e:
            logger.error(f"Error retrieving completion: {e}")
            raise

    async def get_completion_async(self, prompt: str, max_tokens: int = 150) -> str:
        """
        Asynchronously get a text completion for the given prompt.

        Args:
            prompt (str): The prompt to send to the API.
            max_tokens (int): Maximum number of tokens to generate.
            
        Returns:
            str: The generated text completion.
        """
        try:
            return await self.client.get_completion_async(prompt, max_tokens)
        except Exception as e:
            logger.error(f"Error retrieving async completion: {e}")
            raise

    def get_chat_completion(self, messages: List[Dict[str, str]], max_tokens: int = 150) -> str:
        """
        Synchronously get a chat-style completion for the given messages.

        Args:
            messages (List[Dict[str, str]]): A list of messages that represent the chat context.
            max_tokens (int): Maximum tokens for the output message.
            
        Returns:
            str: The generated chat response.
        """
        try:
            return self.client.get_chat_completion(messages, max_tokens)
        except Exception as e:
            logger.error(f"Error retrieving chat completion: {e}")
            raise

    async def get_chat_completion_async(self, messages: List[Dict[str, str]], max_tokens: int = 150) -> str:
        """
        Asynchronously get a chat-style completion for the given messages.

        Args:
            messages (List[Dict[str, str]]): A list of messages that represent the chat context.
            max_tokens (int): Maximum tokens for the output message.
            
        Returns:
            str: The generated chat response.
        """
        try:
            return await self.client.get_chat_completion_async(messages, max_tokens)
        except Exception as e:
            logger.error(f"Error retrieving async chat completion: {e}")
            raise

    def transcribe_audio(self, audio_file_path:str):
        """
            Synchronously transcribe an audio file

            Args:
                audio_file_path (str): Path to the audio file.

            Returns:
                str: The transcribed text.

        """
        try:
            return self.client.transcribe_audio(audio_file_path)
        except Exception as e:
            logger.error("Failed to transcribe audio: %s", e)
    
    async def transcribe_audio_async(self, audio_file_path:str):
        """
            Asynchronously transcribe an audio file

            Args:
                audio_file_path (str): Path to the audio file.

            Returns:
                str: The transcribed text.

        """
        try:
            return self.client.transcribe_audio_async(audio_file_path)
        except Exception as e:
            logger.error("Failed to transcribe audio (asymc): %s", e)
    
    
    def generate_image(self, prompt:str, n: int=1, size: str = "1024x1024"):
        """
            Synchronously transcribe an audio file

            Args:
                prompt (str): The prompt for image generation.
                n (int): Number of images.
                size (str): Size of the generated image(s).

            Returns:
                list: URLs of the generated images.

        """
        try:
            return self.client.generate_image(prompt, n, size)
        except Exception as e:
            logger.error("Failed to generate image: %s", e)

    # - generate_image / generate_image_async

    async def generate_image_async(self, prompt:str, n: int=1, size: str = "1024x1024"):
        """
            Asynchronously transcribe an audio file

            Args:
                prompt (str): The prompt for image generation.
                n (int): Number of images.
                size (str): Size of the generated image(s).

            Returns:
                list: URLs of the generated images.

        """
        try:
            return self.client.generate_image_async(prompt, n, size)
        except Exception as e:
            logger.error("Failed to generate image (async): %s", e)
