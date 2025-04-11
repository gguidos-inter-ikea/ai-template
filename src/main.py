"""
Main entry point for the API.
"""
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from src.base.config.logging_config import setup_logging
from src.base.config.config import settings
from src.base.handlers.json_encoder import CustomJSONEncoder
from src.base.lifespan.lifespan import lifespan
from src.base.system.initialize_app import initialize_app
import logging
import uvicorn.config
import json

# Configure logging before creating the FastAPI app
setup_logging()
logger = logging.getLogger(settings.textsNew.main.logger_name)

logger.info(settings.textsNew.main.starting_application)

# Add log configuration for Uvicorn
uvicorn.config.LOGGING_CONFIG = None  # Disable Uvicorn's default logging config

# Configure FastAPI to use the custom JSON encoder
def custom_json_serializer(*args, **kwargs):
    return json.dumps(*args, cls=CustomJSONEncoder, **kwargs)

# Create the FastAPI app
app = FastAPI(
    title="Template API",
    description="Template API for FastAPI",
    contact={
        "name": settings.application.application_owner,
        "email": settings.application.application_owner_email
    },
    version="0.0.1",
    swagger_ui_parameters={"TryItOutEnabled": True},
    include_in_schema=True,
    lifespan=lifespan,
    default_response_class=JSONResponse,
    json_dumps=custom_json_serializer,
    docs_url="/docs",  # Enable default FastAPI Swagger UI
    redoc_url="/redoc",  # Enable default FastAPI ReDoc
    openapi_url="/openapi.json"  # Enable default FastAPI OpenAPI schema
)

# Delegate the startup process to the startup module
app = initialize_app(app)

logger.info(settings.textsNew.main.application_started)
