from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class AiModelsConfig(BaseSettings):
    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="allow",      # ← was "forbid"
        frozen=True,
    )

    # --- API / endpoint ---
    openai_api_key: str = ""
    openai_url: str = ""

    # --- bulk comma‑separated lists (preferred) ---
    openai_chat_models:   str = "gpt-4o,gpt-4o-mini"
    openai_image_models:  str = "dall-e-3"
    openai_video_models:  str = ""                      # “sora-…”, etc.

    # --- *defaults* for backward‑compat containers ---
    default_chat_model:      str = "gpt-4o"
    default_chat_model_mini: str = "gpt-4o-mini"
    default_embedding_model: str = "text-embedding-ada-002"
    default_whisper_model:   str = "whisper-imc"
    default_image_model:     str = "dall-e-3"

    