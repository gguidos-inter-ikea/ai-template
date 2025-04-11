from typing import Set
from src.base.config.config import settings

class AlertConfig:
    """Configuration for alert types and thresholds."""
    def __init__(
        self,
        enabled_logs: Set[str] = None,
        unauthorized_access_threshold: int = 3,
        rate_limit_threshold: int = 5,
        cooldown_minutes: int = 5,
        time_window_minutes: int = 60
    ):
        """
        Initialize alert configuration.
        
        Args:
            enabled_logs: Set of log files to monitor (e.g., {'security', 'rate_limit', 'error'})
            unauthorized_access_threshold: Number of unauthorized attempts before alerting
            rate_limit_threshold: Number of rate limit violations before alerting
            cooldown_minutes: Minutes to wait between alerts
            time_window_minutes: Time window for tracking events
        """
        self.enabled_logs = set(enabled_logs or settings.enabled_log_types)
        self.unauthorized_access_threshold = unauthorized_access_threshold
        self.rate_limit_threshold = rate_limit_threshold
        self.cooldown_minutes = cooldown_minutes
        self.time_window_minutes = time_window_minutes