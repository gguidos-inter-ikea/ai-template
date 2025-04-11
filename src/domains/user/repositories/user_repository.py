"""
User repository module.
"""
from datetime import datetime
from typing import Dict, Any, List, Optional
from src.base.infrastructure.db.mongoDB.mongo_client import MongoDBClient
from src.base.repositories.mongodb import DBRepository
from src.domains.user.exceptions import DuplicateUserError, UserNotFoundError
from bson import ObjectId

# Define a type alias for better readability
User = Dict[str, Any]

class UserRepository(DBRepository[User]):
    """Repository for performing CRUD operations on the users collection."""

    def __init__(self, client: MongoDBClient):
        """
        Initialize the user repository.
        
        Args:
            client: The MongoDB client
        """
        super().__init__(client, "users")

    def _serialize_document(
        self, 
        document: Optional[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """
        Convert MongoDB document to a JSON-serializable dictionary.
        
        Args:
            document: The MongoDB document to serialize
            
        Returns:
            Optional[Dict[str, Any]]: The serialized document or None
        """
        if document is None:
            return None
            
        # Create a copy to avoid modifying the original
        result = document.copy()
        
        # Convert ObjectId to string
        if "_id" in result and isinstance(result["_id"], ObjectId):
            result["_id"] = str(result["_id"])
            
        # Convert datetime objects to ISO format strings
        for key, value in result.items():
            if isinstance(value, datetime):
                result[key] = value.isoformat()
                
        return result

    # Domain-specific methods that extend the base repository functionality

    async def find_by_email(self, email: str) -> Optional[User]:
        """
        Find a user by their email address.
        
        Args:
            email: The email address to search for
            
        Returns:
            Optional[User]: The user if found, None otherwise
        """
        user = await self.find_one({"email": email})
        return self._serialize_document(user)

    async def find_by_username(self, username: str) -> Optional[User]:
        """
        Find a user by their username.
        
        Args:
            username: The username to search for
            
        Returns:
            Optional[User]: The user if found, None otherwise
        """
        user = await self.find_one({"username": username})
        return self._serialize_document(user)
        
    async def find_active_users(self) -> List[User]:
        """
        Find all active users.
        
        Returns:
            List[User]: List of active users
        """
        users = await self.find({"active": True})
        return [self._serialize_document(user) for user in users]
        
    async def deactivate_user(self, user_id: str) -> bool:
        """
        Deactivate a user account.
        
        Args:
            user_id: The ID of the user to deactivate
            
        Returns:
            bool: True if the user was deactivated, False otherwise
            
        Raises:
            UserNotFoundError: If the user doesn't exist
        """
        # First check if the user exists
        user = await self.find_one({"_id": ObjectId(user_id)})
        if user is None:
            raise UserNotFoundError(user_id)
            
        return await self.update(user_id, {"active": False})
        
    async def change_password(
        self,
        user_id: str,
        hashed_password: str
    ) -> bool:
        """
        Update a user's password.
        
        Args:
            user_id: The ID of the user
            hashed_password: The new hashed password
            
        Returns:
            bool: True if the password was updated, False otherwise
            
        Raises:
            UserNotFoundError: If the user doesn't exist
        """
        # First check if the user exists
        user = await self.find_one({"_id": ObjectId(user_id)})
        if user is None:
            raise UserNotFoundError(user_id)
            
        return await self.update(user_id, {"password": hashed_password})
        
    async def create_user(self, user_data: User) -> str:
        """
        Create a new user with duplicate checking.
        
        Args:
            user_data: The user data to insert
            
        Returns:
            str: The ID of the created user
            
        Raises:
            DuplicateUserError: If a user with the same email or username
            already exists
        """
        # Check for existing user with same email
        if "email" in user_data:
            existing_user = await self.find_by_email(user_data["email"])
            if existing_user is not None:
                raise DuplicateUserError("email", user_data["email"])
            
        # Check for existing user with same username
        if "username" in user_data:
            existing_user = await self.find_by_username(user_data["username"])
            if existing_user is not None:
                raise DuplicateUserError("username", user_data["username"])
            
        # Create the user
        return await self.create(user_data)
        
    async def get_user_by_id(self, user_id: str) -> User:
        """
        Get a user by ID with error handling.
        
        Args:
            user_id: The ID of the user
            
        Returns:
            User: The user data
            
        Raises:
            UserNotFoundError: If the user doesn't exist
        """
        user = await self.find_one({"_id": ObjectId(user_id)})
        if user is None:
            raise UserNotFoundError(user_id)
            
        return self._serialize_document(user)