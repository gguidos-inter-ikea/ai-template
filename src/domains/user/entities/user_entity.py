"""
User entity module.
"""
from src.domains.user.entities.base_entity import BaseEntity
from pydantic import Field, field_validator, model_validator, ConfigDict
from bson import ObjectId
from typing import Optional
import bleach
import re

def sanitize_input(value: str) -> str:
    """
    Sanitize input to remove potentially harmful characters or content.
    This function removes HTML tags and certain special characters that
    may be used for script injection.

    Args:
        value (str): Input string to sanitize.

    Returns:
        str: Sanitized string.
    """
    # Replace HTML tags with an empty string
    sanitized_value = bleach.clean(value, tags=[], attributes={}, strip=True)
    sanitized_value = re.sub(r"[<>\"']", "", sanitized_value)
    return sanitized_value

class ObjectIdStr(str):
    """Custom data type for handling ObjectId as a string."""

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value, field=None):
        """Validate that the value is an ObjectId and return it as a string."""
        if not isinstance(value, ObjectId):
            raise TypeError(f"Expected ObjectId, but got {type(value)} instead.")
        return str(value)

    @classmethod
    def __get_pydantic_json_schema__(cls, schema):
        """Modify the JSON schema to represent ObjectIdStr as a string."""
        schema.update(type="string")
        return schema

class User(BaseEntity):
    id: Optional[ObjectIdStr] = Field(None, alias="_id")
    name: str
    email: str
    age: int

    model_config = ConfigDict(
        populate_by_name=True,  # Allow alias fields to be populated
        arbitrary_types_allowed=True  # Allow custom types like ObjectIdStr
    )

    @model_validator(mode='before')
    @classmethod
    def convert_object_id(cls, values):
        """Convert ObjectId to string if needed."""
        if "_id" in values and isinstance(values["_id"], ObjectId):
            values["id"] = str(values["_id"])
        return values
    
    @field_validator("name")
    def sanitize_name(cls, value):
        """Sanitize the 'name' field to prevent script injection."""
        return sanitize_input(value)

    @field_validator("email")
    def sanitize_email(cls, value):
        """
            Sanitize and validate the 'email' field to prevent malicious
            content.
        """
        # Use bleach to sanitize the email and remove any tags if necessary
        sanitized_email = sanitize_input(value)
        # Ensure the email is a valid format
        if not re.match(r"[^@]+@[^@]+\.[^@]+", sanitized_email):
            raise ValueError(f"Invalid email address: {sanitized_email}")
        return sanitized_email