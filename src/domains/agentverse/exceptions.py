from fastapi import status
from src.base.handlers.exception import DomainException
from src.domains.agentverse.command_room.command_room import CommandRoomTransmitter

class AgentverseDomainException(DomainException):
    """
    Base exception for all errors occurring within the AgentVerse domain.

    Inherits from DomainException to ensure consistent FastAPI error response formatting.
    """
    domain = "agentverse"


class AgentVerseError(Exception):
    """
    Base Python-side exception (non-HTTP) for AgentVerse internal logic errors.

    This is intended for use in situations not tied directly to HTTP responses.
    """
    def __init__(self, message: str, details: dict = None):
        self.message = message
        self.details = details or {}
        super().__init__(message)


# ─────────────────────────────────────────────────────────────
# REGISTRY EXCEPTIONS
# ─────────────────────────────────────────────────────────────

class RegistryError(AgentVerseError):
    """General error raised during registry operations."""
    pass


class RegistrationError(RegistryError):
    """Raised when registration of a component fails."""
    pass


# ─────────────────────────────────────────────────────────────
# DOMAIN-SPECIFIC EXCEPTIONS
# ─────────────────────────────────────────────────────────────

class DuplicateAgentError(AgentverseDomainException):
    """
    Raised when attempting to create an EVA (Agent) that already exists.

    Example:
        - Trying to register an agent with a name that's already taken.
    """

    def __init__(self, field: str, value: str, message: str = None):
        custom_message = message or f"EVA DNA String with {field} '{value}' already presents in AEI"
        super().__init__(
            message=custom_message,
            status_code=status.HTTP_409_CONFLICT,
            error_code="AGENT_DUPLICATE",
            data={
                "field": field,
                "value": value
            }
        )

class BlueprintConflictError(DuplicateAgentError):
    """Alias for duplicate agent detection in blueprinting phase."""
    pass

class UnknownAgentTypeError(AgentverseDomainException):
    """Raised when the requested agent type is not registered."""
    def __init__(self, value: str):
        super().__init__(
            message=f"Unknown EVA prototype type '{value}' – not registered in soul matrix",
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="UNKNOWN_AGENT_TYPE",
            data={
                "field": "type",
                "value": value
            }
        )

class InvalidComponentError(AgentverseDomainException):
    """
    Raised when one or more configuration types (e.g., LLM, DB, cache)
    provided for an EVA agent are not valid or not available in the system.
    """

    def __init__(self, invalid_fields: list[tuple[str, str]]):
        """
        Args:
            invalid_fields (list of tuples): Each tuple is (field, value) of the invalid entry.
        """
        formatted = ", ".join([f"{field}='{value}'" for field, value in invalid_fields])
        message = f"Invalid configuration for EVA: {formatted}"

        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="INVALID_EVA_COMPONENT",
            data={
                "invalid_components": [
                    {"field": field, "value": value}
                    for field, value in invalid_fields
                ]
            }
        )


async def handle_ws_exception(
    commandroom: CommandRoomTransmitter,
    socket_id: str,
    exception: Exception
) -> dict:
    """
    Handle exceptions in WebSocket context without raising HTTP responses.

    Args:
        commandroom: The CommandRoomTransmitter instance.
        socket_id: The socket identifier of the client.
        exception: The raised exception.

    Returns:
        A dictionary with error details that can be sent to the client.
    """
    if isinstance(exception, AgentverseDomainException):
        await commandroom.to_socket(
            socket_id,
            message=f"[NERV] ❌ EVA Failure: {exception.message}"
        )
        return {
            "error": exception.message,
            "code": f"{exception.domain}.{exception.error_code}",
            "data": exception.data
        }
    else:
        await commandroom.to_socket(
            socket_id,
            message="[NERV] 🚨 Unknown exception occurred during EVA orchestration"
        )
        return {
            "error": str(exception),
            "code": "agentverse.UNKNOWN",
            "data": {}
        }