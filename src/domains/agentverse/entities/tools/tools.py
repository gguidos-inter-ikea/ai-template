from pydantic import BaseModel, Field
from typing import Dict, Any

class ToolConfig(BaseModel):
    """
    Base configuration for all tools.
    Extend this for tool-specific settings.
    """
    # Toggle whether the tool is active at runtime
    enabled: bool = Field(
        True,
        description="Whether this tool is enabled (can be turned off for maintenance)."
    )
    # Overall timeout (seconds) for the execute call
    timeout: float = Field(
        30.0,
        description="Max time in seconds before execution is aborted."
    )
    # Optional retry behavior
    retries: int = Field(
        0,
        description="Number of times to retry on transient failure."
    )
    retry_backoff: float = Field(
        0.5,
        description="Base backoff in seconds between retries (exponential)."
    )
    # Freeform metadata for provider-specific settings
    extra: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional provider-specific config."
    )
