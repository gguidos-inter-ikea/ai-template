import openai
import logging
from openai import OpenAIError # You can also catch RateLimitError, APIError, etc.
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type
from src.base.config.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set the API key from your configuration
openai.api_key = settings.ai_models.openai_api_key

class OpenAIClient:
    def __init__(
        self,
        url: str,
        api_key: str,
        model: str,
        model_mini: str,
        embedding_model: str,
        whispering_model: str,
        image_model: str
    ):
        """
        Initializes the OpenAI client.

        Args:
            url (str): Base URL for OpenAI API endpoints (set if using a proxy/alternative endpoint).
            api_key (str): Your OpenAI API key.
            model (str): Model for standard completions.
            model_mini (str): A lighter, less costly model variant.
            embedding_model (str): Model for generating embeddings (e.g., "text-embedding-ada-002").
            whispering_model (str): Model for audio transcription.
            image_model (str): Model for image generation.
        """
        self.url = url
        self.api_key = api_key
        self.model = model
        self.model_mini = model_mini
        self.embedding_model = embedding_model
        self.whispering_model = whispering_model
        self.image_model = image_model

        # Optionally override the API base (for self-hosted endpoints or proxies)
        if self.url:
            openai.api_base = self.url

    # ---------------------------
    # Synchronous methods with retries
    # ---------------------------
    @retry(
        wait=wait_exponential(min=1, max=60),
        stop=stop_after_attempt(6),
        retry=retry_if_exception_type(OpenAIError),
        reraise=True
    )
    def get_embeddings(self, input_text: str):
        """
        Synchronously generate an embedding for the provided text.

        Args:
            input_text (str): The text to embed.
        Returns:
            list: The embedding vector.
        """
        try:
            response = openai.Embedding.create(
                input=input_text,
                model=self.embedding_model
            )
            return response['data'][0]['embedding']
        except OpenAIError as e:
            logger.error("Failed to get embeddings: %s", e)
            raise

    @retry(
        wait=wait_exponential(min=1, max=60),
        stop=stop_after_attempt(6),
        retry=retry_if_exception_type(OpenAIError),
        reraise=True
    )
    def get_completion(self, prompt: str, max_tokens: int = 150):
        """
        Synchronously generate a text completion from a prompt.
        
        Args:
            prompt (str): The prompt to send.
            max_tokens (int): Maximum tokens to generate.
        Returns:
            str: The generated text.
        """
        try:
            response = openai.Completion.create(
                engine=self.model,
                prompt=prompt,
                max_tokens=max_tokens
            )
            text = response['choices'][0]['text'].strip()
            return text
        except OpenAIError as e:
            logger.error("Failed to get completion: %s", e)
            raise

    @retry(
        wait=wait_exponential(min=1, max=60),
        stop=stop_after_attempt(6),
        retry=retry_if_exception_type(OpenAIError),
        reraise=True
    )
    def get_chat_completion(self, messages: list, max_tokens: int = 150):
        """
        Synchronously generate a chat-style response.
        
        Args:
            messages (list): List of message dicts (e.g., [{"role": "system", "content": "You are a helpful assistant."}, ...]).
            max_tokens (int): Maximum tokens to generate.
        Returns:
            str: The chat response.
        """
        try:
            response = openai.ChatCompletion.create(
                model=self.model,  # Optionally, set a dedicated chat model here.
                messages=messages,
                max_tokens=max_tokens
            )
            message_content = response['choices'][0]['message']['content'].strip()
            return message_content
        except OpenAIError as e:
            logger.error("Failed to get chat completion: %s", e)
            raise

    @retry(
        wait=wait_exponential(min=1, max=60),
        stop=stop_after_attempt(6),
        retry=retry_if_exception_type(OpenAIError),
        reraise=True
    )
    def transcribe_audio(self, audio_file_path: str):
        """
        Synchronously transcribe an audio file using the Whisper model.
        
        Args:
            audio_file_path (str): Path to the audio file.
        Returns:
            str: The transcribed text.
        """
        try:
            with open(audio_file_path, "rb") as audio_file:
                response = openai.Audio.transcribe(
                    model=self.whispering_model,
                    file=audio_file
                )
            return response['text']
        except OpenAIError as e:
            logger.error("Failed to transcribe audio: %s", e)
            raise

    @retry(
        wait=wait_exponential(min=1, max=60),
        stop=stop_after_attempt(6),
        retry=retry_if_exception_type(OpenAIError),
        reraise=True
    )
    def generate_image(self, prompt: str, n: int = 1, size: str = "1024x1024"):
        """
        Synchronously generate an image based on a given prompt.
        
        Args:
            prompt (str): The prompt for image generation.
            n (int): Number of images.
            size (str): Size of the generated image(s).
        Returns:
            list: URLs of the generated images.
        """
        try:
            response = openai.Image.create(
                prompt=prompt,
                n=n,
                size=size
            )
            image_urls = [data['url'] for data in response['data']]
            return image_urls
        except OpenAIError as e:
            logger.error("Failed to generate image: %s", e)
            raise

    # ---------------------------
    # Asynchronous methods with retries
    # ---------------------------
    @retry(
        wait=wait_exponential(min=1, max=60),
        stop=stop_after_attempt(6),
        retry=retry_if_exception_type(OpenAIError),
        reraise=True
    )
    async def get_embeddings_async(self, input_text: str):
        """
        Asynchronously generate an embedding for the provided text.

        Args:
            input_text (str): The text to embed.
        Returns:
            list: The embedding vector.
        """
        try:
            response = await openai.Embedding.acreate(
                input=input_text,
                model=self.embedding_model
            )
            return response['data'][0]['embedding']
        except OpenAIError as e:
            logger.error("Failed to get embeddings (async): %s", e)
            raise

    @retry(
        wait=wait_exponential(min=1, max=60),
        stop=stop_after_attempt(6),
        retry=retry_if_exception_type(OpenAIError),
        reraise=True
    )
    async def get_completion_async(self, prompt: str, max_tokens: int = 150):
        """
        Asynchronously generate a text completion from a prompt.
        
        Args:
            prompt (str): The prompt to send.
            max_tokens (int): Maximum tokens to generate.
        Returns:
            str: The generated text.
        """
        try:
            response = await openai.Completion.acreate(
                engine=self.model,
                prompt=prompt,
                max_tokens=max_tokens
            )
            text = response['choices'][0]['text'].strip()
            return text
        except OpenAIError as e:
            logger.error("Failed to get completion (async): %s", e)
            raise

    @retry(
        wait=wait_exponential(min=1, max=60),
        stop=stop_after_attempt(6),
        retry=retry_if_exception_type(OpenAIError),
        reraise=True
    )
    async def get_chat_completion_async(self, messages: list, max_tokens: int = 150):
        """
        Asynchronously generate a chat-style response.
        
        Args:
            messages (list): List of message dicts.
            max_tokens (int): Maximum tokens to generate.
        Returns:
            str: The chat response.
        """
        try:
            response = await openai.ChatCompletion.acreate(
                model=self.model,  # You can use a dedicated chat model if preferred.
                messages=messages,
                max_tokens=max_tokens
            )
            message_content = response['choices'][0]['message']['content'].strip()
            return message_content
        except OpenAIError as e:
            logger.error("Failed to get chat completion (async): %s", e)
            raise

    @retry(
        wait=wait_exponential(min=1, max=60),
        stop=stop_after_attempt(6),
        retry=retry_if_exception_type(OpenAIError),
        reraise=True
    )
    async def transcribe_audio_async(self, audio_file_path: str):
        """
        Asynchronously transcribe an audio file using the Whisper model.
        
        Args:
            audio_file_path (str): Path to the audio file.
        Returns:
            str: The transcribed text.
        """
        try:
            # Opening file synchronously; for true async file I/O, consider using aiofiles.
            with open(audio_file_path, "rb") as audio_file:
                response = await openai.Audio.atranscribe(
                    model=self.whispering_model,
                    file=audio_file
                )
            return response['text']
        except OpenAIError as e:
            logger.error("Failed to transcribe audio (async): %s", e)
            raise

    @retry(
        wait=wait_exponential(min=1, max=60),
        stop=stop_after_attempt(6),
        retry=retry_if_exception_type(OpenAIError),
        reraise=True
    )
    async def generate_image_async(self, prompt: str, n: int = 1, size: str = "1024x1024"):
        """
        Asynchronously generate an image based on a given prompt.
        
        Args:
            prompt (str): The prompt for image generation.
            n (int): Number of images.
            size (str): Size of the generated image(s).
        Returns:
            list: URLs of the generated images.
        """
        try:
            response = await openai.Image.acreate(
                prompt=prompt,
                n=n,
                size=size
            )
            image_urls = [data['url'] for data in response['data']]
            return image_urls
        except OpenAIError as e:
            logger.error("Failed to generate image (async): %s", e)
            raise
