from typing import List, Dict
from src.base.config.log_config import LogConfig

def get_default_observable_log_types() -> List[str]:
    """Get the default observable log types."""
    return ["security", "rate_limit", "error"]

class MonitoringSettings:
    """
    Monitoring and observability settings.
    """

    observable_log_types: List[str] = get_default_observable_log_types()

    def __init__(self, log_config: LogConfig):
        """
        Initialize MonitoringSettings with LogConfig as a dependency.

        Args:
            log_config (LogConfig): The LogConfig instance providing
            log-related settings.
        """
        self.log_config = log_config

    @property
    def observable_log_paths(self) -> Dict[str, str]:
        """
        Get the paths for observable logs based on the configured
        log types.
        """
        all_log_paths = {
            "error": self.log_config.error_log_path,
            "security": self.log_config.security_log_path,
            "rate_limit": self.log_config.rate_limit_log_path,
        }
        return {
            log_type: path
            for log_type, path in all_log_paths.items()
            if log_type in get_default_observable_log_types()
        }