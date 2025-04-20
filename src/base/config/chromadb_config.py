from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class ChromaDBSettings(BaseSettings):
    """
    Chromadb-related settings.
    """
    model_config = ConfigDict(
        frozen=True,
        env_file=".env",
        case_sensitive=False,
        extra="allow"
    )
    chromadb_path: str = "/chroma"