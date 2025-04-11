"""
User domain package.
This module contains all functionality related to user management.
"""
from fastapi import FastAPI

def register_routes(app: FastAPI):
    """
    Register user domain routes with the FastAPI application.
    
    Args:
        app: The FastAPI application
    """
    # Import the router here to avoid circular imports
    from domains.user.interfaces.api.v1.controller import router as user_router
    
    # Register the user router with a prefix
    app.include_router(user_router, prefix="/api/v1", tags=["User"]) 