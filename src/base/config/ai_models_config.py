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

    imc_azure_openai_api_key_se: str = ""
    logger.info("Initializing AiModelsConfig {imc_azure_openai_api_key_se}".format(imc_azure_openai_api_key_se=imc_azure_openai_api_key_se))
    openai_key: str = imc_azure_openai_api_key_se
    imc_azure_openai_endpoint_se: str = ""
    openai_endpoint: str = imc_azure_openai_endpoint_se
    model_mini: str = "gpt-4o-mini-imc"
    model: str = "gpt-4o"
    model_batch: str = "gpt-4o-mini-batch"
    model_o1: str = ""
    openai_version: str = "2024-08-01-preview"
    image_model: str = "dall-e-3"
    image_version: str = "2024-02-01"
    whispering_model: str = "whisper-imc"
    whispering_version: str = "2024-06-01"

    llm_config: dict = {
        "config_list": [
            {
                "model": model,
                "api_type": "azure",
                "api_key": openai_key,
                "base_url": openai_endpoint,
                "api_version": openai_version
            }
        ]
    }