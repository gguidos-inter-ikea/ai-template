from typing import List, Union
from datetime import datetime
from pydantic import BaseModel
from src.domains.agentverse.entities.agent_soul_protocol import AgentSoulProtocol  # Adjust if needed


def generate_personality_context(profile: Union[BaseModel, dict]) -> str:
    """
    Generate a formatted context string from any AgentSoulProtocol or compatible dict.

    Args:
        profile (Union[BaseModel, dict]): A Pydantic model instance or dictionary.

    Returns:
        str: The full string-based context ready for LLM injection.
    """
    # Ensure profile is an AgentSoulProtocol instance
    if isinstance(profile, dict):
        profile = AgentSoulProtocol(**profile)

    lines: List[str] = [
        f"# AgentSoulProtocol Context for {getattr(profile, 'name', 'Unnamed EVA')}",
        f"Description: {getattr(profile, 'description', 'No description provided')}",
        f"Origin: {getattr(profile, 'origin', 'Unknown')}",
        f"Created At: {getattr(profile, 'created_at', datetime.now()).isoformat()}",
        "",
        "## Personality Traits"
    ]

    skip_fields = {"name", "description", "origin", "created_at", "metadata"}

    for field_name in profile.model_fields:
        if field_name in skip_fields:
            continue

        value = getattr(profile, field_name, None)
        if value is None:
            continue

        if isinstance(value, list):
            value_str = ", ".join(map(str, value))
        elif isinstance(value, dict):
            value_str = "; ".join(f"{k}: {v}" for k, v in value.items())
        else:
            value_str = str(value)

        pretty_name = field_name.replace("_", " ").title()
        lines.append(f"{pretty_name}: {value_str}")

    metadata = getattr(profile, "metadata", {})
    if metadata:
        lines.append("\n## Metadata")
        for k, v in metadata.items():
            lines.append(f"{k}: {v}")

    return "\n".join(lines)
