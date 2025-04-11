import logging
from typing import List, Optional
from langchain.schema.document import Document
from src.base.infrastructure.db.chromaDB.chromadb_client import ChromaDBClient

logger = logging.getLogger(__name__)

class ChromaDBRepository:
    def __init__(
            self,
            chromadb_client: ChromaDBClient
    ):
        self.chromadb_client = chromadb_client

    def add_documents(self, new_chunks: List[Document], ids: List[str]) -> bool:
        """
            Add documents to the Chroma vector store and persist changes.

            Args:
                documents (List[Document]): List of Document objects to be added.
                ids (List[str]): Corresponding list of unique identifiers for the documents.

            Returns:
                bool: True if the documents were added and persisted successfully; False otherwise.
        """
        try:
            return self.chromadb_client.add_documents(documents=new_chunks, ids=ids)
        except Exception as e:
            logger.error(e)

    def get_documents(self, include: Optional[List[str]] = None) -> List[Document]:
        """
        Retrieve documents from the Chroma vector store.

        Args:
            include (Optional[List[str]]): List of fields to include (e.g., metadata).

        Returns:
            List[Document]: A list of Document objects retrieved from the store.
        """
        try:
            return self.chromadb_client.get_documents(include)
        except Exception as e:
            logger.error(e)

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
            return self.chromadb_client.clear_collection(collection_name)
        except Exception as e:
            logger.error(e)