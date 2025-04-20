import logging
from dependency_injector import containers, providers
from src.base.infrastructure.db.chromaDB.utils.create_embedding_function import (
    create_embedding_function
)
from src.base.repositories.chromadb_repository import ChromaDBRepository
from src.base.infrastructure.db.chromaDB.chromadb_client import ChromaDBClient
from src.base.config.config import settings

logger = logging.getLogger(__name__)

class ChromaDBContainer(containers.DeclarativeContainer):
    
    chromadb_client = providers.Singleton(
        ChromaDBClient,
        chroma_path=settings.chromadb.chromadb_path,
        embedding_function=create_embedding_function
    )

    chromadb_repository = providers.Singleton(
        ChromaDBRepository,
        chromadb_client=chromadb_client
    )
