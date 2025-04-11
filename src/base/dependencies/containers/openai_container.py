import logging
from dependency_injector import containers, providers
from src.base.config.config import settings
from src.base.infrastructure.ai.openai_client import OpenAIClient
from src.base.repositories.openai_repository import OpenAIRepository

logger = logging.getLogger(__name__)

class OpenAIContainer(containers.DeclarativeContainer):
    """
    Container for OpenAI-related dependencies.
    """
    logger.info("Initializing OpenAIContainer")

    openai_client = providers.Singleton(
        OpenAIClient,
        url=settings.ai_models.url,
        api_key=settings.ai_models.api_key,
        embedding_model=settings.ai_models.embedding_model,
        whispering_model=settings.ai_models.whispering_model,
        image_model=settings.ai_models.image_model,
        model=settings.ai_models.model,
        model_mini=settings.ai_models.model_mini
    )

    openai_repository = providers.Factory(
        OpenAIRepository,
        openai_client=openai_client
    )
