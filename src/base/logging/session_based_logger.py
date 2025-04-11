from fastapi import FastAPI
from fastapi.routing import APIRoute
import logging

logger = logging.getLogger("Decorator Logger")
def log_session_based_endpoints(app: FastAPI):
    for route in app.routes:
        if isinstance(route, APIRoute):
            endpoint = route.endpoint
            if getattr(endpoint, "__session_based__", False):
                logger.info(f"Session-based endpoint registered: {route.path} -> {endpoint.__name__}")