from src.base.config.utils.utils import resolve_path, parse_comma_separated_list
from pydantic import field_validator
import logging

class LogConfig:
    """
    Logging and observability settings.
    """
    @field_validator('email_recipients', mode='before')
    @classmethod
    def parse_email_recipients(cls, v):
        return parse_comma_separated_list(v)
    
    security_log_path: str = resolve_path(
        "SECURITY_LOG_PATH",
        "logs/security.log"
    )
    
    error_log_path: str = resolve_path("ERROR_LOG_PATH", "logs/errors.log")
    rate_limit_log_path: str = resolve_path(
        "RATE_LIMIT_LOG_PATH",
        "logs/rate_limiter.log"
    )
    security_log_to_file: bool = True
    error_log_to_file: bool = True
    rate_limit_log_to_file: bool = True
    security_log_level: str = "WARNING"
    error_log_level: str = "ERROR"
    rate_limit_log_level: str = "INFO"
    

    
    def get_log_level(level_str: str) -> int:
        """Convert string log level to logging module constant."""
        log_levels = {
            "CRITICAL": logging.CRITICAL,
            "ERROR": logging.ERROR,
            "WARNING": logging.WARNING,
            "INFO": logging.INFO,
            "DEBUG": logging.DEBUG
        }
        return log_levels.get(level_str.upper(), logging.INFO)