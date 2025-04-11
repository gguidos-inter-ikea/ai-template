"""
User domain-specific exceptions.
"""
from fastapi import status
from src.base.handlers.exception import DomainException

class UserDomainException(DomainException):
    """Base exception for user domain errors."""
    domain = "user"

class DuplicateUserError(UserDomainException):
    """Exception raised when trying to create a user that already exists."""
    
    def __init__(self, field: str, value: str, message: str = None):
        """
        Initialize the exception.
        
        Args:
            field: The field that caused the duplication
            (e.g., 'email', 'username')
            value: The value that's duplicated
            message: Optional custom message
        """
        if message is None:
            message = f"User with {field} '{value}' already exists"
        super().__init__(
            message=message,
            status_code=status.HTTP_409_CONFLICT,
            error_code="USER_DUPLICATE",
            data={
                "field": field,
                "value": value
            }
        )

class UserNotFoundError(UserDomainException):
    """Exception raised when a user is not found."""
    
    def __init__(self, user_id: str, message: str = None):
        """
        Initialize the exception.
        
        Args:
            user_id: The ID of the user that wasn't found
            message: Optional custom message
        """
        if message is None:
            message = f"User with ID '{user_id}' not found"
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="USER_NOT_FOUND",
            data={"user_id": user_id}
        )

class InvalidCredentialsError(UserDomainException):
    """Exception raised when login credentials are invalid."""
    
    def __init__(self, message: str = None):
        """
        Initialize the exception.
        
        Args:
            message: Optional custom message
        """
        if message is None:
            message = "Invalid username or password"
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="INVALID_CREDENTIALS"
        ) 