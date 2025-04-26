# src/core/agentverse/tools/guardrail_tool.py

import re
import logging
from typing import List
from src.domains.agentverse.tools.base import BaseTool, ToolResult, ToolConfig
from src.domains.agentverse.registries import tool_registry_instance as tool_registry

logger = logging.getLogger(__name__)

class GuardrailToolConfig(ToolConfig):
    """Configuration for the GuardrailTool"""
    # If input contains any of these, reject outright
    banned_phrases: List[str] = ["forbidden", "drop table"]
    # If input contains any of these, mask them
    mask_phrases:   List[str] = ["secret", "password"]

@tool_registry.register(
    name="guardrail",
    description="Filter or reject incoming user requests according to policy rules",
    version="1.0.0",
    metadata={"config_schema": "GuardrailToolConfig"}
)
class GuardrailTool(BaseTool):
    name: str = "guardrail"
    version: str = "1.0.0"
    parameters = {
        "content": {
            "type": "string",
            "description": "Text to check and sanitize",
            "required": True
        }
    }

    def __init__(self, config: GuardrailToolConfig = None):
        super().__init__(config=config or GuardrailToolConfig())

    async def execute(self, content: str) -> ToolResult:
        cfg = self.config
        # 1) Reject if any banned phrase is present
        lower = content.lower()
        for phrase in cfg.banned_phrases:
            if phrase.lower() in lower:
                logger.warning(f"Guardrail rejecting content due to banned phrase: {phrase}")
                return ToolResult(
                    success=False,
                    result=None,
                    error=f"Input contains banned content: '{phrase}'"
                )

        # 2) Mask any mask_phrases
        sanitized = content
        for pattern in cfg.mask_phrases:
            sanitized = re.sub(
                pattern, 
                "[redacted]", 
                sanitized, 
                flags=re.IGNORECASE
            )

        return ToolResult(success=True, result=sanitized)
