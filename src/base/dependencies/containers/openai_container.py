# src/base/dependencies/containers/openai_container.py
import logging
from dependency_injector import containers, providers
from src.base.config.ai_models_config import AiModelsConfig
from src.base.infrastructure.ai.utils.build_llm_repositories import (
    build_openai_repositories,
)

logger    = logging.getLogger(__name__)
settings  = AiModelsConfig()
repos_map = build_openai_repositories(settings)     
default_slug = settings.default_chat_model
default_chat_slug = settings.openai_chat_models.split(",")[0].strip()

class OpenAIContainer(containers.DeclarativeContainer):
    repositories = providers.Object(repos_map)

    default_openai_repository = providers.Callable(
        lambda repo_dict: repo_dict["llm"][default_slug],
        repositories,
    )

    default_openai_client = providers.Callable(
        lambda repo: repo.client,
        default_openai_repository,
    )
