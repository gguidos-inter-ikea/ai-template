from src.base.config.application_config import ApplicationConfig
from src.base.config.cache_settings import CacheSettings
from src.base.config.db_settings import DatabaseSettings
from src.base.config.event_config import EventConfig
from src.base.config.log_config import LogConfig
from src.base.config.messaging_config import MessagingConfig
from src.base.config.monitoring_settings import MonitoringSettings
from src.base.config.security_config import SecurityConfig

class Settings:
    """
    Aggregated settings for the application.
    """

    def __init__(self, event_config: EventConfig):
        self.event_config = event_config
    
    application = ApplicationConfig()
    cache = CacheSettings()
    database = DatabaseSettings()
    messaging = MessagingConfig()
    monitoring = MonitoringSettings()
    logging = LogConfig()
    security = SecurityConfig()