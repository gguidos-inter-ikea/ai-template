#!/usr/bin/env python
"""
Database connection test script.

This script tests connections to MongoDB and Redis, providing clear error messages
when connections fail. It's useful for troubleshooting connection issues without
starting the entire application.

Usage:
  python -m src.scripts.test_db_connection
  python -m src.scripts.test_db_connection --mongodb
  python -m src.scripts.test_db_connection --redis
"""
import asyncio
import argparse
import sys
import os
from pathlib import Path
import colorama
from colorama import Fore, Style

# Add the parent directory to the path so we can import from src
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

async def test_mongodb_connection():
    """Test the MongoDB connection."""
    from src.base.config.config import settings
    from src.base.infrastructure.db.mongoDB.mongo_client import MongoDBClient
    from src.base.infrastructure.exceptions import MongoDBConnectionError
    
    print(f"{Fore.BLUE}Testing MongoDB connection...{Style.RESET_ALL}")
    print(f"  Host: {settings.mongodb_uri}")
    print(f"  Database: {settings.mongodb_dbname}")
    
    try:
        # Create and connect to MongoDB
        client = MongoDBClient(settings.mongodb_uri, settings.mongodb_dbname)
        await client.connect()
        
        # Test a simple command
        await client.client.admin.command('ping')
        
        print(f"{Fore.GREEN}✓ MongoDB connection successful!{Style.RESET_ALL}")
        
        # Test the specified database
        collections = await client.client[settings.mongodb_dbname].list_collection_names()
        print(f"  Found {len(collections)} collections in database '{settings.mongodb_dbname}':")
        for collection in collections:
            print(f"    - {collection}")
        
        # Disconnect
        await client.disconnect()
        return True
        
    except MongoDBConnectionError as e:
        print(f"{Fore.RED}✗ MongoDB connection failed: {e.message}{Style.RESET_ALL}")
        print(f"  Details: {e.data.get('error_details', 'No detailed error available')}")
        print("\nTroubleshooting tips:")
        print("  1. Check if MongoDB is running")
        print("  2. Verify the connection string in your .env file")
        print("  3. Check network connectivity between your application and MongoDB")
        print("  4. For Docker: ensure the MongoDB service is defined and healthy")
        return False
        
    except Exception as e:
        print(f"{Fore.RED}✗ Unexpected error connecting to MongoDB: {str(e)}{Style.RESET_ALL}")
        return False

async def test_redis_connection():
    """Test the Redis connection."""
    from src.base.config.config import settings
    from src.base.infrastructure.exceptions import RedisConnectionError
    import aioredis
    
    print(f"{Fore.BLUE}Testing Redis connection...{Style.RESET_ALL}")
    print(f"  Host: {settings.redis_host}")
    print(f"  Port: {settings.redis_port}")
    print(f"  Database: {settings.redis_db}")
    
    try:
        # Create Redis client
        client = aioredis.Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            db=settings.redis_db,
            password=settings.redis_password,
            encoding="utf-8",
            decode_responses=True
        )
        
        # Test connection
        result = await client.ping()
        
        if result:
            print(f"{Fore.GREEN}✓ Redis connection successful!{Style.RESET_ALL}")
            
            # Get some server info
            info = await client.info()
            print(f"  Redis version: {info.get('redis_version', 'unknown')}")
            print(f"  Connected clients: {info.get('connected_clients', 'unknown')}")
            print(f"  Used memory: {info.get('used_memory_human', 'unknown')}")
            
            # Close connection
            await client.close()
            return True
        else:
            print(f"{Fore.RED}✗ Redis ping returned unexpected result: {result}{Style.RESET_ALL}")
            return False
            
    except aioredis.RedisError as e:
        print(f"{Fore.RED}✗ Redis connection failed: {str(e)}{Style.RESET_ALL}")
        print("\nTroubleshooting tips:")
        print("  1. Check if Redis is running")
        print("  2. Verify the Redis host, port, and password in your .env file")
        print("  3. Check network connectivity between your application and Redis")
        print("  4. For Docker: ensure the Redis service is defined and healthy")
        return False
        
    except Exception as e:
        print(f"{Fore.RED}✗ Unexpected error connecting to Redis: {str(e)}{Style.RESET_ALL}")
        return False

async def main():
    # Initialize colorama
    colorama.init()
    
    parser = argparse.ArgumentParser(description="Test database connections")
    parser.add_argument("--mongodb", action="store_true", help="Test only MongoDB connection")
    parser.add_argument("--redis", action="store_true", help="Test only Redis connection")
    args = parser.parse_args()
    
    # If no specific test is requested, test both
    test_mongodb = args.mongodb or not (args.mongodb or args.redis)
    test_redis = args.redis or not (args.mongodb or args.redis)
    
    success = True
    
    if test_mongodb:
        if not await test_mongodb_connection():
            success = False
        print()  # Add a blank line
        
    if test_redis:
        if not await test_redis_connection():
            success = False
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 