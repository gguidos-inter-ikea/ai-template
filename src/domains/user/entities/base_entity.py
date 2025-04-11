"""
Base entity module.
"""
from pydantic import BaseModel, Field, model_validator, ConfigDict
from datetime import datetime
from typing import Optional


class BaseEntity(BaseModel):
    """Base entity with common fields for all entities."""
    created: Optional[datetime] = Field(default_factory=datetime.utcnow)
    modified: Optional[datetime] = Field(default_factory=datetime.utcnow)
    deleted: Optional[datetime] = None

    model_config = ConfigDict(
        # Configuration to allow aliasing fields and arbitrary types (if needed)
        populate_by_name=True,
        arbitrary_types_allowed=True
    )

    @model_validator(mode='before')
    @classmethod
    def set_modified(cls, values):
        """Automatically update the 'modified' field."""
        values["modified"] = datetime.utcnow()
        return values
