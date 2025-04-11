from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class ApplicationConfig(BaseSettings):
    """
    General application settings.
    """
    model_config = ConfigDict(
        frozen=True,
        env_file=".env",
        case_sensitive=False,
        extra="allow"
    )

    application_name: str = "My API"
    application_owner: str = "Team"
    application_owner_email: str = "team@example.com"
    environment: str = "development"
    api_key: str = ""
    port: int = 8000
    log_level: str = "INFO"