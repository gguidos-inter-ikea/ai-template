from fastapi.middleware.cors import CORSMiddleware
from src.base.middlewares import (
    IPFilterMiddleware,
    LoggingMiddleware,
    RequestIDMiddleware,
    ResponseFormatMiddleware,
    SecurityHeadersMiddleware,
    SessionMiddleware
)
from src.base.middlewares.jwt_middleware import JWTVerificationMiddleware
from src.base.config.config import settings
import logging

logger = logging.getLogger(settings.textsNew.middleware.register["logger_name"])

def register_middleware(app):
    # The order in which middleware are added here determines the processing order.
    # Remember: The last added middleware is the outermost layer.
    #
    # Desired execution order on incoming requests (outermost to innermost):
    #   CORSMiddleware ->
    #   LoggingMiddleware ->
    #   IPFilterMiddleware ->
    #   RequestIDMiddleware ->
    #   JWTVerificationMiddleware ->
    #   (Session Middleware, if added) ->
    #   SecurityHeadersMiddleware ->
    #   ResponseFormatMiddleware ->
    #   Route Handler
    #
    # We add them in reverse order (innermost first):

    # 1. Innermost: ResponseFormatMiddleware
    logger.info(settings.textsNew.middleware.register["initialize_response_formatter"])
    app.add_middleware(ResponseFormatMiddleware)
    
    # 2. Next: SecurityHeadersMiddleware
    logger.info(settings.textsNew.middleware.register["initialize_security_headers"])
    app.add_middleware(SecurityHeadersMiddleware)
    
    # 3. Next: JWTVerificationMiddleware (authentication context)
    logger.info(settings.textsNew.middleware.register["initialize_jwt_verification"])
    app.add_middleware(
        JWTVerificationMiddleware,
        jwt_service=app.container.services.jwt_service(),
        exclude_paths=[
            r"^/favicon.ico",
            r"^/docs",
            r"^/redoc",
            r"^/openapi.json",
            r"^/api/v1/auth/login",
            r"^/internal/",
            r"^/metrics",
            r"^/api/v1/auth/verify-token",
            r"^/api/v1/user/registration",
            r"^/api/v1/users/login",
            r"^/api/v1/users",
            r"^/api/v1/chat"
        ]
    )
    
    # 4. Next: RequestIDMiddleware (assigns unique request IDs)
    logger.info(settings.textsNew.middleware.register["initialize_request"])
    app.add_middleware(RequestIDMiddleware)
    
    # 5. Next: IPFilterMiddleware (blocks disallowed IPs)
    logger.info(settings.textsNew.middleware.register["initialize_ip_filtering"])
    app.add_middleware(
        IPFilterMiddleware,
        allowed_ips=settings.security.allowed_admin_ips,
        protected_paths=["/admin", "/internal"],
        public_paths=[
            "/internal/metrics", 
            "/metrics", 
            "/internal/health",
            "/internal/rate-limit-examples"
        ]
    )
    
    # 6. Next: LoggingMiddleware (logs the full request/response lifecycle)
    logger.info(settings.textsNew.middleware.register["initialize_logging"])
    app.add_middleware(LoggingMiddleware)
    
    # 7. Outermost: CORSMiddleware (applies CORS headers to all responses)
    logger.info(settings.textsNew.middleware.register["initialize_cors"])
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],         # Allow all origins for development
        allow_credentials=True,
        allow_methods=["*"],         # Allow all HTTP methods
        allow_headers=["*"],         # Allow all headers
    )
