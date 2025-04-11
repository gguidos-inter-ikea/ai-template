from pydantic_settings import BaseSettings
from typing import Optional

class CacheSettings(BaseSettings):
    """
    Cache-related settings (e.g., Redis).
    """
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_password: str = ""
    redis_prefix: str = "myapp:"
    redis_db: int = 0
    redis_url: Optional[str] = None