import logging
import logging.config
import json
from pathlib import Path
import logging.handlers
from datetime import datetime

# Create logs directory if it does not exist
Path("logs").mkdir(parents=True, exist_ok=True)

class RequestIdFormatter(logging.Formatter):
    """
    Formatter that ensures there's always a request_id field.
    If not present, uses a default value.
    """
    def format(self, record):
        if not hasattr(record, 'request_id'):
            record.request_id = 'no-request-id'
        return super().format(record)

class SecurityEventFormatter(logging.Formatter):
    """
    Specialized formatter for security events that formats logs as structured JSON
    to match the format of access logs.
    """
    def format(self, record):
        # Start with a base structure for the log entry
        log_data = {
            "timestamp": self.formatTime(record, "%Y-%m-%d %H:%M:%S,%f")[:-3],
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "path": record.pathname,
            "line": record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Extract JSON from the message if present
        message = record.getMessage()
        try:
            message_start = message.find('{')
            message_end = message.rfind('}')
            if message_start != -1 and message_end != -1:
                json_str = message[message_start:message_end + 1]
                event_data = json.loads(json_str)
                
                # Merge event data into the log entry
                for key, value in event_data.items():
                    if key != "message":  # Don't override the original message
                        log_data[key] = value
        except (json.JSONDecodeError, ValueError):
            # If not JSON, keep the original message
            pass
        
        # Format the timestamp in the same style as access logs
        if "timestamp" in log_data and log_data["timestamp"].find('T') != -1:
            # Convert ISO format to space-separated with comma
            try:
                dt = datetime.fromisoformat(log_data["timestamp"].replace('Z', ''))
                log_data["timestamp"] = dt.strftime("%Y-%m-%d %H:%M:%S,%f")[:-3]
            except (ValueError, TypeError):
                pass
            
        return json.dumps(log_data, default=str)

class StructuredJSONFormatter(logging.Formatter):
    """
    Custom formatter that outputs logs as structured JSON with all extra fields.
    """
    def format(self, record):
        log_data = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "path": record.pathname,
            "line": record.lineno,
            "request_id": getattr(record, 'request_id', 'no-request-id')
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add any extra attributes from the LogRecord
        for key, value in record.__dict__.items():
            if key not in ["args", "asctime", "created", "exc_info", "exc_text", "filename",
                           "funcName", "id", "levelname", "levelno", "lineno", "module",
                           "msecs", "message", "msg", "name", "pathname", "process",
                           "processName", "relativeCreated", "stack_info", "thread", "threadName",
                           "request_id"]:
                log_data[key] = value
        
        return json.dumps(log_data, default=str)

class MetricsEndpointFilter(logging.Filter):
    """
    Filter to exclude requests to the metrics endpoint from Uvicorn access logs.
    """
    def __init__(self, excluded_paths=None):
        super().__init__()
        self.excluded_paths = excluded_paths or ["/internal/metrics", "/metrics", "/internal/health"]
    
    def filter(self, record):
        # Check if this is an access log record
        if not hasattr(record, 'args') or not isinstance(record.args, tuple) or len(record.args) < 3:
            return True
        
        # Extract the request path from the log message
        try:
            # In Uvicorn access logs, args[2] contains the request method + path
            # Format: "GET /path HTTP/1.1"
            request_info = record.args[2]
            for path in self.excluded_paths:
                if f" {path}" in request_info or f" {path}/" in request_info:
                    return False  # Filter out this log entry
        except (IndexError, AttributeError):
            pass
        
        return True  # Keep all other log entries

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "()": RequestIdFormatter,
            "format": "%(asctime)s [%(levelname)s] [%(request_id)s] %(name)s: %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "simple": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "json": {
            "()": StructuredJSONFormatter,
        },
        "security": {
            "()": SecurityEventFormatter,
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        }
    },
    "filters": {
        "metrics_endpoint_filter": {
            "()": MetricsEndpointFilter,
        }
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "formatter": "standard",
            "class": "logging.StreamHandler",
        },
        "uvicorn_console": {
            "level": "INFO",
            "formatter": "simple",
            "class": "logging.StreamHandler",
            "filters": ["metrics_endpoint_filter"],
        },
        "file": {
            "level": "INFO",
            "formatter": "json",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "logs/application.log",
            "maxBytes": 10485760,  # 10 MB
            "backupCount": 10,
        },
        "error_file": {
            "level": "ERROR",
            "formatter": "json",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "logs/errors.log",
            "maxBytes": 10485760,  # 10 MB
            "backupCount": 20,
        },
        "access_file": {
            "level": "INFO",
            "formatter": "json",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "logs/access.log",
            "maxBytes": 10485760,  # 10 MB
            "backupCount": 5,
            "filters": ["metrics_endpoint_filter"],
        },
        "business_file": {
            "level": "INFO",
            "formatter": "json",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "logs/business.log",
            "maxBytes": 10485760,  # 10 MB
            "backupCount": 30,  # Keep more business logs
        },
        "db_file": {
            "level": "INFO",
            "formatter": "json",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "logs/db.log",
            "maxBytes": 10485760,  # 10 MB  
            "backupCount": 30,  # Keep more business logs
        },
        "api_file": {
            "level": "INFO",
            "formatter": "json",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "logs/api.log",
            "maxBytes": 10485760,  # 10 MB
            "backupCount": 30,  # Keep more business logs
        },
        "security_file": {
            "level": "WARNING",
            "formatter": "security",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "logs/security.log",
            "maxBytes": 10485760,  # 10 MB
            "backupCount": 30,  # Keep more security logs for audit
        },
        "rate_limiter_file": {
            "level": "WARNING",
            "formatter": "security",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "logs/rate_limiter.log",
            "maxBytes": 10485760,  # 10 MB
            "backupCount": 30,  # Keep more security logs for audit
        },
        "security_monitor_file": {
            "level": "DEBUG",
            "formatter": "standard",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "logs/security_monitor.log",
            "maxBytes": 10485760,  # 10 MB
            "backupCount": 30,  # Keep more security logs for audit
        }
    },
    "loggers": {
        "": {
            "handlers": ["console", "file", "error_file"],
            "level": "DEBUG",
            "propagate": True,
        },
        "agentverse": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False
        },
        "src.base.middlewares.logging": {
            "handlers": ["console", "access_file"],
            "level": "INFO",
            "propagate": False,
        },
        "uvicorn.access": {
            "handlers": ["uvicorn_console", "access_file"],
            "level": "INFO",
            "propagate": False,
        },
        "uvicorn.error": {
            "handlers": ["uvicorn_console", "error_file"],
            "level": "ERROR",
            "propagate": False,
        },
        "pika": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
        "pymongo": {  # Add a separate logger for pymongo
            "handlers": ["console"],
            "level": "WARNING",  # Set the level to WARNING to suppress DEBUG logs
            "propagate": False,
        },
        "business": {
            "handlers": ["console", "business_file"],
            "level": "INFO",
            "propagate": False,
        },
        "database": {
            "handlers": ["console", "db_file"],
            "level": "INFO",
            "propagate": False,
        },
        "external_api": {
            "handlers": ["console", "api_file"],
            "level": "INFO",
            "propagate": False,
        },
        "security": {
            "handlers": ["console", "security_file", "error_file"],
            "level": "WARNING",
            "propagate": False,
        },
        "rate_limiter": {
            "handlers": ["console", "rate_limiter_file", "error_file"],
            "level": "WARNING",
            "propagate": False,
        },
        "security_monitor": {
            "handlers": ["console", "security_monitor_file", "error_file"],
            "level": "DEBUG",
            "propagate": False,
        }
    },
}

def setup_logging():
    """Set up logging configuration."""
    logging.config.dictConfig(LOGGING_CONFIG)
    
    # Apply custom overrides after the main config is loaded
    from src.base.config.logging_override import apply_logging_overrides
    apply_logging_overrides()
