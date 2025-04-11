import logging
import os
from logging.handlers import RotatingFileHandler
from src.base.config.config import settings

# Create logs directory if it doesn't exist
logs_dir = '/app/logs'
os.makedirs(logs_dir, exist_ok=True)

# Configure a special logger for rate limit events
rate_limit_logger = logging.getLogger("rate_limiter")
rate_limit_logger.setLevel(logging.INFO)

# Create a separate handler for the rate limit log file
rate_limit_handler = RotatingFileHandler(
    filename=os.path.join(logs_dir, 'rate_limiter.log'),
    maxBytes=10485760,  # 10MB
    backupCount=10,
    encoding='utf-8'
)

# Define the log format
formatter = logging.Formatter(
    '%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

rate_limit_handler.setFormatter(formatter)
rate_limit_logger.addHandler(rate_limit_handler)

# Prevent log messages from propagating to the root logger
rate_limit_logger.propagate = False

def log_rate_limit_exceeded(endpoint: str, identifier: str, times: int, seconds: int):
    """
    Log when a rate limit is exceeded
    
    Args:
        endpoint: The endpoint that was rate limited
        identifier: The client identifier (IP or API key)
        times: The number of requests allowed
        seconds: The time window in seconds
    """
    rate_limit_logger.warning(
        f"Rate limit exceeded: {endpoint} | Client: {identifier} | Limit: {times}/{seconds}s"
    )

def log_rate_limit_approaching(endpoint: str, identifier: str, current: int, limit: int, seconds: int):
    """
    Log when a client is approaching the rate limit (80% or higher)
    
    Args:
        endpoint: The endpoint being accessed
        identifier: The client identifier (IP or API key)
        current: The current request count
        limit: The maximum requests allowed
        seconds: The time window in seconds
    """
    percentage = (current / limit) * 100
    if percentage >= 80:
        rate_limit_logger.info(
            f"Rate limit approaching: {endpoint} | Client: {identifier} | "
            f"Usage: {current}/{limit} ({percentage:.1f}%) in {seconds}s"
        ) 