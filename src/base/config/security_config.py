from typing import List
from pydantic import field_validator
from src.base.config.utils.utils import parse_comma_separated_list


def get_default_observable_log_types() -> List[str]:
    """Get the default observable log types."""
    return ["security", "rate_limit", "error"]

class SecurityConfig:
    """
    Security and rate-limiting settings.
    """

    @field_validator('email_recipients', mode='before')
    @classmethod
    def parse_email_recipients(cls, v):
        return parse_comma_separated_list(v)
    

    @field_validator('allowed_admin_ips', mode='before')
    @classmethod
    def parse_allowed_admin_ips(cls, v):
        return parse_comma_separated_list(v)
    
    # Allowed admin IPs
    allowed_admin_ips: List[str] = []

    # JWT settings
    jwt_secret_key: str = "your-secret-key"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 30

    # Rate limiting settings
    standard_rate_limit: int = 100
    standard_rate_limit_window: int = 60
    strict_rate_limit: int = 20
    strict_rate_limit_window: int = 60
    very_strict_rate_limit: int = 5
    very_strict_rate_limit_window: int = 60
    rate_limit_suspicious_threshold: int = 5
    monitor_rate_limits: bool = True

    # Security settings
    error_window_minutes: int = 5
    error_threshold: int = 3
    alert_cooldown_minutes: int = 0

    # Alerts
    alerts_enabled: bool = True

    teams_alerts_enabled: bool = False
    teams_webhook_url: str = ""
    teams_alert_threshold: int = 10
    teams_suspicious_ip_threshold: int = 3

    email_alerts_enabled: bool = True
    email_smtp_server: str = "smtp.gmail.com"
    email_smtp_port: int = 587
    email_sender: str = ""
    email_password: str = ""
    email_recipients: List[str] = []
    email_use_tls: bool = True
    email_alert_threshold: int = 3
    email_suspicious_ip_threshold: int = 3

    slack_alerts_enabled: bool = False
    slack_webhook_url: str = ""
    slack_alert_threshold: int = 10
    slack_suspicious_ip_threshold: int = 3