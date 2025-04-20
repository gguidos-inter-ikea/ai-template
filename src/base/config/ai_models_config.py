from pydantic_settings import BaseSettings
from pydantic import ConfigDict

import logging

logger = logging.getLogger(__name__)

class AiModelsConfig(BaseSettings):
    """
    General application settings.
    """
    model_config = ConfigDict(
        frozen=True,
        env_file=".env",
        case_sensitive=False,
        extra="allow"
    )

    openai_api_key: str = ""
    openai_url: str = ""
    model_mini: str = "gpt-4o-mini"
    embedding_model: str = "text-embedding-ada-002"
    model: str = "gpt-4o"
    model_batch: str = "gpt-4o-mini-batch"
    model_o1: str = ""
    openai_version: str = "2024-08-01-preview"
    image_model: str = "dall-e-3"
    image_version: str = "2024-02-01"
    whispering_model: str = "whisper-imc"
    whispering_version: str = "2024-06-01"