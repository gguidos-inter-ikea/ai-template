from typing import Dict, Any, List, Optional, ClassVar
from pydantic import BaseModel, Field
from datetime import datetime
import asyncio

class ToolResult(BaseModel):
    """Result from a tool execution"""
    success: bool
    result: Any
    error: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ToolConfig(BaseModel):
    """
    The *actual* settings for a BaseTool at runtime.
    All tools share these fields, and can extend this class.
    """
    enabled: bool = Field(True, description="Turn the tool on/off without code changes")
    timeout: float = Field(30.0, description="Seconds before cancelling execute()")
    retries: int = Field(0, description="How many times to retry on transient errors")
    retry_backoff: float = Field(0.5, description="Base backoff (seconds) for retries")
    extra: Dict[str, Any] = Field(default_factory=dict, description="Tool-specific settings")

# Tool-related exceptions
class ToolError(Exception):
    """Base class for tool-related errors"""
    pass

class ToolExecutionError(ToolError):
    """Raised when tool execution fails"""
    def __init__(self, message: str, original_error: Optional[Exception] = None):
        super().__init__(message)
        self.original_error = original_error

class ToolAuthenticationError(ToolError):
    """Raised when tool authentication fails"""
    pass

class ToolPermissionError(ToolError):
    """Raised when tool lacks required permissions"""
    pass

class ToolValidationError(ToolError):
    """Raised when tool input validation fails"""
    pass

class ToolDependencyError(ToolError):
    """Raised when tool dependencies are missing or invalid"""
    pass

class BaseTool:
    name: ClassVar[str] = "base_tool"
    parameters: ClassVar[Dict[str, Any]] = {}
    required_permissions: ClassVar[List[str]] = []
    required_dependencies: ClassVar[List[str]] = []

    def __init__(self, config: Optional[ToolConfig] = None, **deps):
        self.config = config or ToolConfig()
        self._validate_dependencies(deps)
        for k, v in deps.items():
            setattr(self, k, v)

    def _validate_dependencies(self, deps):
        missing = set(self.required_dependencies) - deps.keys()
        if missing:
            raise ToolDependencyError(f"Missing: {missing}")

    def _validate_params(self, params):
        # check against self.parameters schema,
        # raise ToolValidationError on failure
        pass

    async def execute(self, **params) -> ToolResult:
        if not self.config.enabled:
            raise ToolExecutionError("Tool disabled")
        self._validate_params(params)
        # permissions check here...
        try:
            # enforce timeout
            result = await asyncio.wait_for(self._run(**params),
                                            timeout=self.config.timeout)
            return ToolResult(success=True, result=result)
        except ToolError as te:
            return ToolResult(success=False, error=str(te))
        except asyncio.TimeoutError:
            return ToolResult(success=False, error="Execution timed out")
        except Exception as e:
            raise ToolExecutionError("Execution failed", e)

    async def _run(self, **params) -> Any:
        """Override in subclasses."""
        raise NotImplementedError
