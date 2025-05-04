from collections import defaultdict
from src.base.infrastructure.ai.openai_client import OpenAIClient
from src.base.repositories.openai_repository import OpenAIRepository
from src.base.config.ai_models_config import AiModelsConfig

def _repo_for(slug: str, cfg: AiModelsConfig) -> OpenAIRepository:
    return OpenAIRepository(OpenAIClient(
        url             = cfg.openai_url,
        api_key         = cfg.openai_api_key,
        model           = slug,                         # ← the slug IS the chat/image/video model
        model_mini      = slug,
        embedding_model = cfg.default_embedding_model,
        whispering_model= cfg.default_whisper_model,
        image_model     = slug
    ))

def build_openai_repositories(cfg: AiModelsConfig) -> dict[str, dict[str, OpenAIRepository]]:
    buckets: dict[str, dict[str, OpenAIRepository]] = defaultdict(dict)

    for slug in cfg.openai_chat_models.split(","):
        slug = slug.strip()
        if slug:
            buckets["llm"][slug] = _repo_for(slug, cfg)

    for slug in cfg.openai_image_models.split(","):
        slug = slug.strip()
        if slug:
            buckets["image"][slug] = _repo_for(slug, cfg)

    for slug in cfg.openai_video_models.split(","):
        slug = slug.strip()
        if slug:
            buckets["video"][slug] = _repo_for(slug, cfg)

    return buckets