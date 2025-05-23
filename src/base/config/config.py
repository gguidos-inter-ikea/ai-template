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
from src.base.config.sacred_keys import SacredKeys
class Settings:
    """
    Aggregated settings for the application.
    """
    def __init__(self):
        self.event_config: EventConfig = EventConfig(self)
        self.ai_models: AiModelsConfig = AiModelsConfig()
        self.application: ApplicationConfig = ApplicationConfig()
        self.cache: CacheSettings = CacheSettings()
        self.database: DatabaseSettings = DatabaseSettings()
        self.logging: LogConfig = LogConfig()
        self.messaging: MessagingConfig = MessagingConfig()
        self.monitoring: MonitoringSettings = MonitoringSettings(self.logging)
        self.security: SecurityConfig = SecurityConfig()
        self.texts = TextConfig()
        self.textsNew = TextConfigNew()
        self.chromadb: ChromaDBSettings = ChromaDBSettings()
        self.sacred_keys: SacredKeys = SacredKeys()

settings = Settings()
