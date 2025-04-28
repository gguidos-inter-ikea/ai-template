from typing import Dict, Any, List, Generic, TypeVar, Optional
from datetime import datetime
from src.base.infrastructure.db.mongoDB.mongo_client import MongoDBClient
from motor.motor_asyncio import AsyncIOMotorCollection
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=Dict[str, Any])

class MongoDBRepository(Generic[T]):
    """
    Generic repository to interact with MongoDB collections.
    This serves as an optional base class for domain-specific repositories
    that want to inherit common CRUD operations.
    """

    def __init__(self, client: MongoDBClient):
        """
        Initialize the repository.
        
        Args:
            client: The MongoDB client
            collection_name: The name of the collection this repository will work with
        """
        self.client = client
        self.collection = None
        
    async def ensure_connected(self, collection_name:str):
        """
        Ensure that the MongoDB client is connected and the collection is available.
        This should be called before any repository operation.
        
        Returns:
            AsyncIOMotorCollection: The MongoDB collection
            
        Raises:
            ValueError: If the connection cannot be established
        """
        if self.collection is None:
            logger.debug(f"Setting up collection {collection_name}")
            if self.client is None:
                logger.error("MongoDB client is None")
                raise ValueError("MongoDB client is not available")
                
            # Check if the client is connected and connect if needed
            try:
                # Use explicit 'is None' check for 'db' attribute
                if not hasattr(self.client, 'db') or self.client.db is None:
                    logger.debug("MongoDB client not connected, connecting now")
                    await self.client.connect()
                
                self.collection = self.client.get_collection(collection_name)
                logger.debug(f"Successfully obtained collection {collection_name}")
            except Exception as e:
                logger.error(f"Error getting collection {collection_name}: {str(e)}")
                raise ValueError(f"Failed to connect to MongoDB: {str(e)}")
        
        return self.collection

    async def create(self, data: T, collection_name: str) -> str:
        """
        Create a new document and return the agent's `agent_id` field instead of Mongo `_id`.
        """
        collection = await self.ensure_connected(collection_name)
        data_copy = data.copy()

        # Clean _id if present but None
        if "_id" in data_copy and data_copy["_id"] is None:
            del data_copy["_id"]

        # Add timestamps
        now = datetime.now()
        data_copy["created"] = data_copy.get("created", now)
        data_copy["modified"] = data_copy.get("modified", now)

        await self.client.insert_one(data_copy, collection)

        return data_copy  # ✅ Return the agent's id

    async def find_all(self, collection_name: str) -> List[T]:
        """
        Retrieve all documents from the collection.
        
        Returns:
            List[T]: All documents in the collection
        """
        # Ensure we have a valid collection
        collection = await self.ensure_connected(collection_name)
            
        return await self.client.find({}, collection)

    async def find(self, query: Dict[str, Any], collection_name:str) -> List[T]:
        """
        Retrieve documents that match the specified query.

        Args:
            query: A dictionary representing the query to be executed

        Returns:
            List[T]: A list of documents that match the query
        """
        # Ensure we have a valid collection
        collection = await self.ensure_connected(collection_name)
            
        return await self.client.find(query, collection)
        
    async def find_one(self, query: Dict[str, Any], collection_name: str) -> Optional[T]:
        """
        Find a single document matching the query.
        
        Args:
            query: A dictionary representing the query to be executed
            
        Returns:
            Optional[T]: The matching document or None if not found
        """
        # Ensure we have a valid collection
        collection = await self.ensure_connected(collection_name)
            
        return await self.client.find_one(query, collection)

    async def update(self, doc_id: str, data: Dict[str, Any], collection_name: str) -> bool:
        """
        Update a document by ID.
        
        Args:
            doc_id: The ID of the document to update
            data: The new data to apply
            
        Returns:
            bool: True if the update was successful, False otherwise
        """
        # Ensure we have a valid collection
        collection = await self.ensure_connected(collection_name)
            
        # Ensure _id is not included in the update data
        if "_id" in data:
            del data["_id"]
        
        # Add modified timestamp
        data.update({"modified": datetime.utcnow()})
        
        # Construct the update document
        update_doc = {"$set": data}
        
        # Execute the update
        result = await self.client.update_one(
            {"_id": ObjectId(doc_id)}, 
            update_doc,
            collection
        )
        
        # Check if anything was updated
        return result.matched_count > 0

    async def delete(self, doc_id: str, collection_name: str) -> bool:
        """
        Delete a document by ID.
        
        Args:
            doc_id: The ID of the document to delete
            
        Returns:
            bool: True if the document was deleted, False otherwise
        """
        # Ensure we have a valid collection
        collection = await self.ensure_connected(collection_name)
            
        result = await self.client.delete_one(
            {"_id": ObjectId(doc_id)},
            collection
        )
        
        # Check if anything was deleted
        return result > 0
        
    async def get_collection(self, collection_name:str) -> AsyncIOMotorCollection:
        """
        Get the underlying collection object.
        
        Returns:
            AsyncIOMotorCollection: The MongoDB collection
            
        Raises:
            ValueError: If the collection is not available
        """
        return await self.ensure_connected(collection_name)