from dependency_injector import containers, providers
from src.base.infrastructure.db.mongoDB.mongo_client import MongoDBClient
from src.base.repositories.mongodb import DBRepository
from src.base.config.config import settings

class DatabaseContainer(containers.DeclarativeContainer):
    """
    Container for database-related dependencies.
    """
    # MongoDB client
    mongo_client = providers.Singleton(
        MongoDBClient,
        db_uri=settings.database.mongodb_uri,
        db_name=settings.database.mongodb_dbname,
    )

    # Generic repository factory
    db_repository_factory = providers.Factory(
        DBRepository,
        client=mongo_client
    )