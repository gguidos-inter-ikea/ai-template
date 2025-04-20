from src.base.config.ai_models_config import AiModelsConfig
from src.base.config.application_config import ApplicationConfig
from src.base.config.cache_settings import CacheSettings
from src.base.config.db_settings import DatabaseSettings
from src.base.config.event_config import EventConfig
from src.base.config.log_config import LogConfig
from src.base.config.messaging_config import MessagingConfig
from src.base.config.monitoring_settings import MonitoringSettings
from src.base.config.security_config import SecurityConfig
from src.base.config.text_config import TextConfig
from src.base.config.text.config import TextConfigNew
from src.base.config.chromadb_config import ChromaDBSettings
class Settings:
    """
    Aggregated settings for the application.
    """
    def __init__(self):
        self.event_config = EventConfig(self)
        self.ai_models = AiModelsConfig()
        self.application = ApplicationConfig()
        self.cache = CacheSettings()
        self.database = DatabaseSettings()
        self.logging = LogConfig()
        self.messaging = MessagingConfig()
        self.monitoring = MonitoringSettings(self.logging)
        self.security = SecurityConfig()
        self.texts = TextConfig()
        self.textsNew = TextConfigNew()
        self.chromadb = ChromaDBSettings()

settings = Settings()
