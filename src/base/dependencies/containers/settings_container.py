from dependency_injector import containers, providers
from src.base.config.config import Settings

class SettingsContainer(containers.DeclarativeContainer):
    """
    Container for settings-related dependencies.
    """
    settings = providers.Singleton(
        Settings
    )