from openai import OpenAI
from typing import List, Dict, Optional
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class OpenAIClient:
    """
    Wrapper for OpenAI API operations including chat, completion, embeddings, audio, and image generation.
    """

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
        if not api_key.startswith("sk-"):
            raise ValueError("Invalid OpenAI API key")

        self.client = OpenAI(api_key=api_key, base_url=url)
        self.url = url

        self.model = model
        self.model_mini = model_mini
        self.embedding_model = embedding_model
        self.whispering_model = whispering_model
        self.image_model = image_model

        logger.info(f"🔑 OpenAIClient initialized — base_url: {url}, model: {model}")

    def get_chat_completion(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 150
    ) -> str:
        try:
            logger.info(f"[ChatCompletion] Model: {self.model}, Messages: {messages}")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            import traceback
            logger.error(f"[ChatCompletion] Error: {e}")
            logger.debug(traceback.format_exc())
            raise

    def get_completion(
        self,
        prompt: str,
        model: Optional[str] = None,
        max_tokens: int = 150
    ) -> str:
        model = model or self.model_mini
        logger.debug(f"[Completion] Model: {model}, Prompt: {prompt}")
        try:
            response = self.client.completions.create(
                model=model,
                prompt=prompt,
                max_tokens=max_tokens
            )
            return response.choices[0].text.strip()
        except Exception as e:
            logger.error(f"[Completion] Error: {e}")
            raise

    def get_embeddings(self, text: str, model: Optional[str] = None) -> List[float]:
        model = model or self.embedding_model
        logger.debug(f"[Embeddings] Model: {model}, Input: {text}")
        try:
            response = self.client.embeddings.create(
                model=model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"[Embeddings] Error: {e}")
            raise

    def generate_image(
        self,
        prompt: str,
        n: int = 1,
        size: str = "1024x1024",
        model: Optional[str] = None
    ) -> List[str]:
        model = model or self.image_model
        logger.debug(f"[ImageGeneration] Model: {model}, Prompt: {prompt}, Count: {n}, Size: {size}")
        try:
            response = self.client.images.generate(
                model=model,
                prompt=prompt,
                n=n,
                size=size
            )
            urls = [img.url for img in response.data]
            logger.debug(f"[ImageGeneration] URLs: {urls}")
            return urls
        except Exception as e:
            logger.error(f"[ImageGeneration] Error: {e}")
            raise

    def transcribe_audio(self, audio_file_path: str, model: Optional[str] = None) -> str:
        model = model or self.whispering_model
        logger.debug(f"[Transcription] Model: {model}, File: {audio_file_path}")

        try:
            with open(Path(audio_file_path), "rb") as audio_file:
                response = self.client.audio.transcriptions.create(
                    model=model,
                    file=audio_file
                )
            return response.text
        except Exception as e:
            logger.error(f"[Transcription] Error: {e}")
            raise
