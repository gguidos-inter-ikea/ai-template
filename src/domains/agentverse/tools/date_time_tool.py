from datetime import datetime
from typing import Dict, Any, ClassVar, Optional
import pytz
import logging

from src.domains.agentverse.tools.base import (
    BaseTool,
    ToolResult,
    ToolConfig,
    ToolExecutionError,
)
from src.domains.agentverse.registries import tool_registry_instance as tool_registry

logger = logging.getLogger(__name__)

class DateTimeToolConfig(ToolConfig):
    """DateTime tool specific configuration"""
    default_timezone: str = "UTC"
    default_format: str = "%Y-%m-%d %H:%M:%S"
    allow_future_dates: bool = True
    max_past_years: int = 100

@tool_registry.register(
    name="Datetime Tool",
    description="Tool for datetime operations and formatting",
    version="1.0.0",
    metadata={"config_schema": "DateTimeToolConfig"},
)
class DateTimeTool(BaseTool):
    """Tool for datetime operations and formatting
    Get current time, format dates, calculate time differences, and handle timezones.
    Useful for time-based queries and calculations.
    """
    name: ClassVar[str] = "datetime"
    version: ClassVar[str] = "1.1.0"
    required_permissions: ClassVar[list] = []
    parameters: ClassVar[Dict[str, Any]] = {
        "format": {
            "type": "string",
            "description": "Output datetime format",
            "default": "%Y-%m-%d %H:%M:%S"
        }
    }

    def __init__(self, config: Optional[DateTimeToolConfig] = None):
        super().__init__(config=config or DateTimeToolConfig())

    def _validate_timezone(self, timezone: str) -> str:
        try:
            return str(pytz.timezone(timezone))
        except Exception:
            logger.error(f"Invalid timezone {timezone}, falling back to {self.config.default_timezone}")
            return self.config.default_timezone

    def _validate_format(self, fmt: str) -> str:
        try:
            datetime.now().strftime(fmt)
            return fmt
        except Exception:
            logger.warning(f"Invalid datetime format '{fmt}', using default '{self.config.default_format}'")
            return self.config.default_format

    async def execute(self, format: str = None) -> ToolResult:
        fmt = self._validate_format(format or self.config.default_format)
        try:
            now = datetime.now(pytz.timezone(self.config.default_timezone))
            formatted = now.strftime(fmt)
            return ToolResult(
                success=True,
                result=formatted,
                metadata={"format": fmt, "timezone": self.config.default_timezone}
            )
        except Exception as e:
            raise ToolExecutionError(f"Failed to get current time: {e}")

    def _format_time_diff(self, days: int, hours: int, minutes: int, seconds: int) -> str:
        parts = []
        if days:
            parts.append(f"{days} day{'s' if days != 1 else ''}")
        if hours:
            parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
        if minutes:
            parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
        if seconds or not parts:
            parts.append(f"{seconds} second{'s' if seconds != 1 else ''}")
        return ", ".join(parts)
