from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from src.base.system.routes import setup_internal_routes
from src.base.middlewares.register_middleware import register_middleware
from src.base.handlers.exception import register_exception_handlers
from src.base.handlers.log_event_handlers import register_event_handlers
from src.domains import initialize_domains
from src.base.routing.auto_routing import register_all_routers
from src.base.dependencies.di_container import Container
from src.base.config.config import settings
from src.base.logging.session_based_logger import log_session_based_endpoints
import os
import logging

logger = logging.getLogger(settings.textsNew.initializers.app["logger_name"])

def initialize_app(app: FastAPI) -> FastAPI:
    """
    Initialize the FastAPI app with all necessary configurations, routes, and middleware.

    Args:
        app (FastAPI): The FastAPI application instance.

    Returns:
        FastAPI: The configured FastAPI application instance.
    """
    # Create and configure the dependency injection container
    logger.info(settings.textsNew.initializers.app["initialize_server"])
    container = Container()

    # Initialize resources (if needed)
    if hasattr(container, 'init_resources'):
        container.init_resources()

    # Initialize domain-specific containers
    logger.info(settings.textsNew.initializers.app["initialize_business_domains"])
    container = initialize_domains(container)

    # Attach the container to the app
    logger.info(settings.textsNew.initializers.app["attaching_di"])
    app.container = container

    # Register domain routes
    logger.info(settings.textsNew.initializers.app["registering_domain_routes"])
    # register_domain_routes(app)
    DOMAINS_PATH = os.path.abspath("src/domains")
    BASE_MODULE = "src.domains"  # Base Python module
    register_all_routers(app, DOMAINS_PATH, BASE_MODULE)

    # Log observable log types
    observable_log_types_text = (
        settings.textsNew.initializers
        .app["initialize_observable_log_types"]
    )
    log_types = settings.monitoring.observable_log_types
    logger.info(f"{observable_log_types_text}".format(log_types=log_types))

    # Integrate Prometheus metrics with basic configuration
    logger.info(
        settings.textsNew.initializers
        .app["integrating_prometheus_metrics"]
    )
    instrumentator = Instrumentator()
    instrumentator.instrument(app)

    # Setup internal routes
    logger.info(
    settings.textsNew.initializers
        .app["registering_event_handlers"]
    )
    setup_internal_routes(app, instrumentator)

    # Register event handlers
    logger.info(
        settings.textsNew.initializers
        .app["registering_exception_handlers"]
    )
    register_event_handlers()

    # Register exception handlers
    logger.info(
        settings.textsNew.initializers
        .app["registering_internal_routes"]
    )
    register_exception_handlers(app)

    # Register middleware
    logger.info(
        settings.textsNew.initializers
        .app["registering_middleware"]
    )
    register_middleware(app)
    log_session_based_endpoints(app)

    logger.info(
        settings.textsNew.initializers
        .app["server_initialized"]
    )
    return app