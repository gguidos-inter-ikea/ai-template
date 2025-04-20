from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection
from typing import Dict, Any, List, Optional
import logging
from src.base.infrastructure.exceptions import MongoDBConnectionError

logger = logging.getLogger("mongodb client")

class MongoDBClient:
    def __init__(self, db_uri: str, db_name: str):
        """
        Initialize the MongoDB client.

        Args:
            db_uri (str): MongoDB URI.
            db_name (str): Database name.
        """
        self.client = None  # Initialize as None to avoid connection during initialization
        self.db = None
        self.db_uri = db_uri
        self.db_name = db_name
        self.collection = None

    async def connect(self) -> None:
        """
        Establish a connection to the MongoDB server.
        
        Raises:
            MongoDBConnectionError: If connection to MongoDB fails
        """
        try:
            if self.client is None:
                # Create a new MongoDB client and connect to the database
                self.client = AsyncIOMotorClient(self.db_uri)
                # Force a connection to test it's working
                await self.client.admin.command('ping')
                self.db = self.client[self.db_name]
                logger.info(f"Connected to database '{self.db_name}' at '{self.db_uri}'")
            else:
                # Test existing connection
                await self.client.admin.command('ping')
                logger.info(f"Connected to database '{self.db_name}' at '{self.db_uri}'")
        except Exception as e:
            # Log detailed error information
            error_msg = str(e)
            logger.error(f"Failed to connect to MongoDB: {error_msg}")
            
            # Raise custom exception with better error handling
            raise MongoDBConnectionError(
                host=self.db_uri,
                error_details=error_msg,
                message="Database connection failed. Please check your MongoDB configuration and ensure the server is running."
            ) from e

    async def disconnect(self) -> None:
        """Close the MongoDB connection."""
        if self.client is not None:
            self.client.close()
            logger.info("Disconnected from MongoDB.")

    def get_collection(self, collection_name: str) -> AsyncIOMotorCollection:
        """
        Dynamically retrieve a collection object.
        
        Args:
            collection_name: The name of the collection to retrieve
            
        Returns:
            AsyncIOMotorCollection: The requested collection
            
        Raises:
            MongoDBConnectionError: If the database connection is not established
        """
        if self.db is None:
            raise MongoDBConnectionError(
                host=self.db_uri, 
                message="Database connection not established. Call 'connect()' first."
            )
        return self.db[collection_name]

    async def insert_one(self, document: Dict[str, Any], collection: AsyncIOMotorCollection) -> Any:
        """
        Insert a single document into a specified collection.
        
        Args:
            document (Dict[str, Any]): The document to insert
            collection (AsyncIOMotorCollection): The collection object
            
        Returns:
            Any: The inserted document ID
        """
        try:
            result = await collection.insert_one(document)
            return result.inserted_id
        except Exception as e:
            logger.error(f"Error inserting document: {str(e)}")
            # Re-raise with more context if needed
            raise

    async def find(self, query: Dict[str, Any], collection: AsyncIOMotorCollection) -> List[Dict[str, Any]]:
        """
        Find documents in the specified collection that match the query.
        
        Args:
            query (Dict[str, Any]): The query criteria
            collection (AsyncIOMotorCollection): The collection object
            
        Returns:
            List[Dict[str, Any]]: List of matching documents
        """
        try:
            documents = await collection.find(query).to_list(length=None)
            sanitized = [self.sanitize_document(doc) for doc in documents]
            return sanitized
        except Exception as e:
            logger.error(f"Error finding documents: {str(e)}")
            raise

    async def find_one(self, query: Dict[str, Any], collection: AsyncIOMotorCollection) -> Optional[Dict[str, Any]]:
        """
        Find a single document in the specified collection that matches the query.
        
        Args:
            query (Dict[str, Any]): The query criteria
            collection (AsyncIOMotorCollection): The collection object
            
        Returns:
            Dict[str, Any]: The matching document or None
        """
        try:
            document = await collection.find_one(query)
            if (document):
                document = self.sanitize_document(document)
            return document
        except Exception as e:
            logger.error(f"Error finding document: {str(e)}")
            raise

    async def update_one(self, query: Dict[str, Any], update: Dict[str, Any], collection: AsyncIOMotorCollection) -> Any:
        """
        Update a single document in the specified collection that matches the query.
        
        Args:
            query (Dict[str, Any]): The query criteria
            update (Dict[str, Any]): The update operations
            collection (AsyncIOMotorCollection): The collection object
            
        Returns:
            Any: The update result
        """
        try:
            result = await collection.update_one(query, update)
            return result
        except Exception as e:
            logger.error(f"Error updating document: {str(e)}")
            raise

    async def delete_one(self, query: Dict[str, Any], collection: AsyncIOMotorCollection) -> int:
        """
        Delete a single document from the specified collection that matches the query.
        
        Args:
            query (Dict[str, Any]): The query criteria
            collection (AsyncIOMotorCollection): The collection object
            
        Returns:
            int: The number of documents deleted
        """
        try:
            result = await collection.delete_one(query)
            return result.deleted_count
        except Exception as e:
            logger.error(f"Error deleting document: {str(e)}")
            raise

    def sanitize_document(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """Converts non-serializable fields like ObjectId to strings."""
        if '_id' in document:
            document['_id'] = str(document['_id'])
        return document
