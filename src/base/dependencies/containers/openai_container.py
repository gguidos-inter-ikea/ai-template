import logging
from dependency_injector import containers, providers
from src.base.config.config import settings
from openai import AzureOpenAI

logger = logging.getLogger(__name__)

class AzureOpenAIWrapper:
    def __init__(self, azure_endpoint: str, api_key: str, api_version: str):
        self.azure_endpoint = azure_endpoint
        self.api_key = api_key
        self.api_version = api_version
        self.client = AzureOpenAI(
            azure_endpoint=azure_endpoint,
            api_key=api_key,
            api_version=api_version
        )
    
    def __getattr__(self, name: str):
        # Delegate attribute lookup to the wrapped client
        return getattr(self.client, name)

class OpenAIContainer(containers.DeclarativeContainer):
    """
    Container for OpenAI-related dependencies.
    """
    logger.info("Initializing OpenAIContainer")
    openai_client = providers.Singleton(
        AzureOpenAI,
        azure_endpoint = settings.ai_models.imc_azure_openai_endpoint_se, # or config.openai_endpoint()
        api_key = settings.ai_models.imc_azure_openai_api_key_se,             # or config.openai_key()
        api_version = settings.ai_models.openai_version      # or config.openai_version()
    )

    audio_client = providers.Singleton(
        AzureOpenAI,
        azure_endpoint = settings.ai_models.openai_endpoint,    # same endpoint
        api_key = settings.ai_models.openai_key,                # same key
        api_version = settings.ai_models.whispering_version      # fixed version for audio, as required
    )
