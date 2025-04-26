from typing import Dict, Any, ClassVar, Optional
import logging

from src.domains.agentverse.tools.base import BaseTool, ToolResult, ToolConfig, ToolExecutionError
from src.domains.agentverse.registries import tool_registry_instance as tool_registry

logger = logging.getLogger(__name__)

class SummarizationToolConfig(ToolConfig):
    """Configuration for the SummarizationTool"""
    model_name: Optional[str] = None  # use default LLM model if None
    temperature: float = 0.0
    max_tokens: int = 256
    style: str = "bullets"  # default style for summary

@tool_registry.register(
    name="summarize",
    description="Summarize arbitrary text via LLM",
    version="1.0.0",
    metadata={"config_schema": "SummarizationToolConfig"},
)
class SummarizationTool(BaseTool):
    """Tool for generating summaries of provided text using an LLM."""
    Config = SummarizationToolConfig
    name: ClassVar[str] = "summarize"
    description: ClassVar[str] = (
        "Summarize text inputs into bullet points or paragraphs using the LLM."
    )
    version: ClassVar[str] = "1.0.0"
    required_permissions: ClassVar[list] = []
    parameters: ClassVar[Dict[str, Any]] = {
        "text": {"type": "string", "description": "Text to summarize", "required": True},
        "style": {"type": "string", "enum": ["bullets", "paragraph"], "default": "bullets"}
    }

    def __init__(self, config: Optional[SummarizationToolConfig] = None, llm=None):
        super().__init__(config=config or SummarizationToolConfig(), llm=llm)
        if not self.llm:
            raise ToolExecutionError("LLM client not provided for SummarizationTool")

    async def execute(self, text: str, style: Optional[str] = None) -> ToolResult:
        # Choose style
        style = style or self.config.style
        if style not in ("bullets", "paragraph"):
            style = self.config.style

        # Build prompt
        prompt = (
            f"Please summarize the following text in {style} style:\n\n{text}"
        )
        try:
            # Call LLM
            response = await self.llm.generate_response(
                prompt=prompt,
                model=self.config.model_name,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens
            )
            return ToolResult(success=True, result=response.content, metadata={"style": style})
        except Exception as e:
            logger.error(f"Summarization failed: {e}")
            raise ToolExecutionError(f"SummarizationTool execution error: {e}")