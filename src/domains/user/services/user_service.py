"""
User service for handling user-related business logic.
"""
from typing import Dict, Any, List, Optional
from src.domains.user.repositories.user_repository import UserRepository, User
from src.domains.user.exceptions import InvalidCredentialsError
import hashlib
import secrets
import logging

logger = logging.getLogger(__name__)

class UserService:
    """Service for managing users and related operations."""
    
    def __init__(
        self, repository: UserRepository,
        request_id: Optional[str] = None
    ):
        """
        Initialize the user service.
        
        Args:
            repository: The user repository
            request_id: The request ID (optional)
        """
        self.repository = repository
        self.request_id = request_id
        
    async def get_users(self) -> List[User]:
        """
        Get all users.
        
        Returns:
            List[User]: List of all users
        """
        logger.info(f"Getting all users (request_id: {self.request_id})")
        logger.debug(f"Repository: {self.repository}")
        if self.repository.client is not None:
            logger.debug(f"Repository client: {self.repository.client}")
        else:
            logger.warning("Repository client is None")
            
        if self.repository.collection is not None:
            logger.debug(f"Repository collection: {self.repository.collection}")
        else:
            logger.warning("Repository collection is None")
        
        users = await self.repository.find_active_users()
        
        # Don't return password hashes
        for user in users:
            if "password" in user:
                del user["password"]
                
        return users
        
    async def create_user(self, user_data: Dict[str, Any]) -> str:
        """
        Create a new user with validation and secure password handling.
        
        Args:
            user_data: The user data including email, username, password, etc.
            
        Returns:
            str: The ID of the created user
            
        Raises:
            DuplicateUserError: If a user with the same email/username already exists
        """
        # Hash the password if provided
        if "password" in user_data:
            user_data["password"] = self._hash_password(user_data["password"])
            
        # Set default values
        user_data["active"] = user_data.get("active", True)
        
        # Create the user (repository will check for duplicates)
        user_id = await self.repository.create_user(user_data)
        logger.info(f"Created new user with ID {user_id}")
        
        return user_id
        
    async def authenticate_user(self, username: str, password: str) -> User:
        """
        Authenticate a user with username/email and password.
        
        Args:
            username: The username or email
            password: The plain text password
            
        Returns:
            User: The authenticated user data
            
        Raises:
            InvalidCredentialsError: If authentication fails
        """
        # Find user by username or email
        user = await self.repository.find_one({
            "$or": [
                {"username": username},
                {"email": username}
            ]
        }, 'users')
        
        # Check if user exists and is active
        if user is None or not user.get("active", True):
            # Use a consistent error message regardless of whether user exists
            # to prevent username enumeration
            raise InvalidCredentialsError()
            
        # Verify password
        if not self._verify_password(password, user["password"]):
            raise InvalidCredentialsError()
        
        # Make sure the user object is properly serialized
        serialized_user = self.repository._serialize_document(user)
            
        # Don't return the password hash
        if "password" in serialized_user:
            del serialized_user["password"]
            
        return serialized_user
        
    async def get_user_by_id(self, user_id: str) -> User:
        """
        Get a user by ID.
        
        Args:
            user_id: The ID of the user
            
        Returns:
            User: The user data
            
        Raises:
            UserNotFoundError: If the user doesn't exist
        """
        return await self.repository.get_user_by_id(user_id)
        
    async def update_user(self, user_id: str, user_data: Dict[str, Any]) -> bool:
        """
        Update a user's information.
        
        Args:
            user_id: The ID of the user to update
            user_data: The updated user data
            
        Returns:
            bool: True if the update was successful
            
        Raises:
            UserNotFoundError: If the user doesn't exist
        """
        # Hash the password if it's being updated
        if "password" in user_data:
            user_data["password"] = self._hash_password(user_data["password"])
            
        # Ensure the user exists (will raise UserNotFoundError if not)
        await self.repository.get_user_by_id(user_id)
        
        # Update the user
        return await self.repository.update(user_id, user_data)
        
    def _hash_password(self, password: str) -> str:
        """
        Hash a password securely.
        
        Args:
            password: The plain text password
            
        Returns:
            str: The secure hash with salt
        """
        # In a real application, use a proper password hashing library like bcrypt or argon2
        # This is a simplified example using hashlib
        salt = secrets.token_hex(16)  # Generate a random salt
        hash = hashlib.sha256(f"{password}{salt}".encode()).hexdigest()
        return f"{salt}${hash}"  # Store salt along with hash
        
    def _verify_password(self, password: str, stored_hash: str) -> bool:
        """
        Verify a password against a stored hash.
        
        Args:
            password: The plain text password to check
            stored_hash: The stored password hash from the database
            
        Returns:
            bool: True if the password matches
        """
        # Split the stored value to get the salt
        try:
            salt, hash = stored_hash.split('$')
            # Compute hash with the same salt
            computed_hash = hashlib.sha256(f"{password}{salt}".encode()).hexdigest()
            # Compare the computed hash with the stored hash
            return computed_hash == hash
        except:
            # If the stored hash doesn't have the expected format
            return False 