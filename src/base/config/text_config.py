class TextConfig:
    # Main
    main = {
        "logger_name": "main",
        "starting_application": "Starting application",
        "application_started": "Application started"
    }

    initialize_app = {
        "logger_name": "initialize app",
        "initialize_server": "Bootstrapping server",
        "initialize_di": "Initializing dependency injection container",
        "attaching_di": "Attaching dependency injection container to the app",
        "initialize_business_domains": "Initializing business domains",
        "initialize_observable_log_types": "Observable log types: {log_types}",
        "integrating_prometheus_metrics": "Integrating Prometheus metrics",
        "registering_event_handlers": "Registering event handlers",
        "registering_exception_handlers": "Registering exception handlers",
        "registering_internal_routes": "Registering internal routes",
        "registering_domain_routes": "Registering domain routes",
        "registering_middleware": "Registering middlewares",
        "server_initialized": "Server bootstrapped successfully"
    }

    # Server initialization
    initialize_server = "Bootstrapping server"
    initialize_di = "Initializing dependency injection container"
    attaching_di = "Attaching dependency injection container to the app"
    initialize_business_domains = "Initializing business domains"
    initialize_observable_log_types = "Observable log types: "
    integrating_prometheus_metrics = "Integrating Prometheus metrics"
    registering_event_handlers = "Registering event handlers"
    registering_exception_handlers = "Registering exception handlers"
    registering_internal_routes = "Registering internal routes"
    registering_domain_routes = "Registering domain routes"
    registering_middleware = "Registering middleware"
    server_initialized = "Server bootstrapped successfully"

    #JWT Middleware
    jwt_verification_middleware = {
        "logger_name": "JWT Middleware",
        "middleware_initialized": (
            "JWT Verification Middleware initialized with "
            "{excluded_paths} excluded paths"
        ),
        "verifying_request": "Verifying request",
        "excluding_paths": "Excluding paths"
    }
    jwt_middleware = "JWT Middleware"
    jwt_middleware_initialized = (
        "JWT Verification Middleware initialized with "
        "{excluded_paths} excluded paths"
    )    
    jwt_verifying_request = "Verifying request"

    # Event Handlers

    event_handlers={
        "registered": "Event handlers registered successfully."
    }
    
    
    # Lifespan events