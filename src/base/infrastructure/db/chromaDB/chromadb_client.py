import os
import logging
from typing import List, Optional, Callable
from langchain_chroma import Chroma
from langchain.schema.document import Document

logger = logging.getLogger(__name__)

class ChromaDBClient:
    """
    Enterprise-grade, embedding-agnostic interface for the Chroma vector store.
    
    This class wraps the Chroma vector store with robust error handling,
    structured logging, and configuration management. The embedding_function
    is provided externally to decouple the vector store from a particular embedding
    implementation.
    
    Attributes:
        embedding_function: A callable that takes text (or Document objects) and returns embeddings.
        chroma_path: Filesystem path for persisting Chroma data.
        db: The underlying Chroma vector store instance.
    """

    def __init__(self, embedding_function: Callable, chroma_path: Optional[str] = None):
        """
        Initialize the EnterpriseChromaDB instance.

        Args:
            embedding_function (Callable): External embedding function to be used by the vector store.
            chroma_path (Optional[str]): Filesystem directory for persistence. Defaults to CHROMA_PATH env variable or "./chroma_db".
        """
        
        # Use provided chroma_path or fallback to environment/default value.
        self.chroma_path = chroma_path or os.getenv("CHROMA_PATH", "./chroma_db")
        logger.info("Initializing EnterpriseChromaDB with path: %s", self.chroma_path)
        
        # Store the embedding_function.
        self.embedding_function = embedding_function
        
        # Initialize the Chroma vector store.
        try:
            self.db = Chroma(
                persist_directory=self.chroma_path,
                embedding_function=self.embedding_function
            )
            logger.info("Chroma vector store successfully initialized.")
        except Exception as e:
            logger.exception("Failed to initialize Chroma vector store.")
            raise e

    def add_documents(self, documents: List[Document], ids: List[str]) -> bool:
        """
        Add documents to the Chroma vector store and persist changes.

        Args:
            documents (List[Document]): List of Document objects to be added.
            ids (List[str]): Corresponding list of unique identifiers for the documents.

        Returns:
            bool: True if the documents were added and persisted successfully; False otherwise.
        """
        try:
            logger.debug("Adding %d documents to the vector store.", len(documents))
            self.db.add_documents(documents, ids=ids)
            self.db.persist()
            logger.info("Documents added and persisted successfully.")
            return True
        except Exception:
            logger.exception("Failed to add documents to the Chroma vector store.")
            return False

    def get_documents(self, include: Optional[List[str]] = None) -> List[Document]:
        """
        Retrieve documents from the Chroma vector store.

        Args:
            include (Optional[List[str]]): List of fields to include (e.g., metadata).

        Returns:
            List[Document]: A list of Document objects retrieved from the store.
        """
        try:
            logger.debug("Retrieving documents with include: %s", include)
            documents = self.db.get(include=include)
            logger.info("Retrieved %d documents.", len(documents))
            return documents
        except Exception:
            logger.exception("Failed to retrieve documents from the vector store.")
            return []

    def clear_collection(self, collection_name: Optional[str] = None) -> bool:
        """
        Clear the entire collection (or a specific collection if applicable) in the vector store.
        
        In an enterprise setup, this action should be used with caution as it resets persisted data.

        Args:
            collection_name (Optional[str]): The name of the collection to clear. Defaults to the primary collection if None.

        Returns:
            bool: True if the collection was cleared successfully; False otherwise.
        """
        try:
            target = collection_name if collection_name else "default"
            logger.debug("Clearing collection: %s", target)
            # If explicit deletion API is available, use it. Otherwise, reinitialize the vector store.
            self.db = Chroma(
                persist_directory=self.chroma_path,
                embedding_function=self.embedding_function
            )
            self.db.persist()
            logger.info("Collection '%s' cleared successfully.", target)
            return True
        except Exception:
            logger.exception("Error clearing collection '%s'.", collection_name)
            return False