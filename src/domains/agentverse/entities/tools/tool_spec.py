from typing import Any, Dict, Optional
from pydantic import BaseModel, Field

class ToolSpec(BaseModel):
    """
    How an agent *declares* it wants to wear a tool:
    
    - `name`: must match a registered BaseTool.name
    - `config`: a raw dict of any overrides (will be merged into the tool’s real ToolConfig)
    """
    name: str
    config: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Per-agent overrides for this tool’s default config"
    )
