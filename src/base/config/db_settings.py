from pydantic_settings import BaseSettings
from typing import Optional

class DatabaseSettings(BaseSettings):
    """
    Database-related settings.
    """
    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_dbname: str = "mydb"
    mongodb_enabled: bool = True