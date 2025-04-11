"""
JWT Verification Middleware.

This middleware automatically verifies JWT tokens in requests and sets
authenticated user information in the request state for protected routes.
"""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from dependency_injector.wiring import inject
from src.base.services.jwt_service import JWTService
from src.base.middlewares.utils.jwt_utils import is_path_excluded
from src.base.middlewares.utils.response_generator import generate_unauthorized_response
from src.base.logging.security_logger import log_unauthorized_access
from src.base.config.config import settings
import logging
import re
import platform

logger = logging.getLogger(
    settings.textsNew.middleware
    .jwt_verification_middleware["logger_name"]
)

@inject
class JWTVerificationMiddleware(BaseHTTPMiddleware):
    """
    Middleware that automatically verifies JWT tokens in requests headers
    and makes the user information available in the request state.
    """
    
    def __init__(
        self, 
        app: ASGIApp, 
        jwt_service: JWTService,
        exclude_paths: list[str] = None,
        auth_header: str = "Authorization",
    ):
        """
        Initialize the JWT verification middleware.
        
        Args:
            app: The ASGI application
            jwt_service: The JWT service for token verification
            exclude_paths: List of path regex patterns to exclude from JWT verification
            auth_header: The header name to extract the JWT token from
        """
        super().__init__(app)
        self.jwt_service = jwt_service
        self.exclude_paths = exclude_paths or [
            r"^/docs",
            r"^/redoc",
            r"^/openapi.json",
            r"^/api/v1/auth/login",
            r"^/internal/",
            r"^/metrics",
            r"^/api/v1/auth/verify-token",
            r"^/api/v1/user/registration"
        ]
        self.auth_header = auth_header
        logger.info(
            settings.textsNew.middleware
            .jwt_verification_middleware["middleware_initialized"]
            .format(excluded_paths=len(self.exclude_paths))
        )

    def is_path_excluded(self, path: str) -> bool:
            """Check if a path should be excluded from JWT verification."""
            for pattern in self.exclude_paths:
                if re.match(pattern, path):
                    return True
            return False
    
    def _is_localhost(self, request: Request) -> bool:
        """
        Check if the request is coming from localhost.
        
        Args:
            request: The FastAPI request object
            
        Returns:
            bool: True if the request is from localhost
        """
        host = request.headers.get("host", "")
        return host.startswith("localhost:") or host.startswith("127.0.0.1:")
    
    async def dispatch(self, request: Request, call_next):
        """
        Process the request and verify JWT token if present.
        
        Args:
            request: The incoming request
            call_next: The next middleware or route handler in the chain
            
        Returns:
            The response from the next middleware or route handler
        """
        # Don't verify JWT for excluded paths
        logger.info(
            settings.texts.jwt_verification_middleware["verifying_request"]
        )
        logger.info(
            settings.texts.jwt_verification_middleware["excluding_paths"]
        )
        
        if self.is_path_excluded(request.url.path):
            logger.info(
                settings.textsNew.middleware
                .jwt_verification_middleware["excluded_path"]
                .format(excluded_path=request.url.path)
            )
            return await call_next(request)
            
        # Extract the JWT token from the Authorization header
        auth_header = request.headers.get(self.auth_header)
 
        if not auth_header:
            logger.warning(
                settings.textsNew.middleware
                .jwt_verification_middleware["no_header"]
                .format(auth_header=self.auth_header, url_path=request.url.path)
            )

            await log_unauthorized_access(
                request=request,
                reason="missing_auth_header",
                additional_info={
                    "required_header": self.auth_header
                }
            )
            
            response = {
                "success": False,
                "statusCode": status.HTTP_401_UNAUTHORIZED,
                "message": (
                    settings.textsNew.middleware
                    .jwt_verification_middleware["missing_header_msg"]
                )
            }
            
            # Add development information for localhost
            if self._is_localhost(request):
                response["pythonVersion"] = platform.python_version()
                response["systemVersion"] = platform.platform()
                
            # Add documentation links
            response["OpenApi-JSON-Documentation"] = f"{request.base_url}v3/api-docs"
            response["OpenApi-Documentation"] = f"{request.base_url}swagger-ui/index.html"
            
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content=response,
                headers={"WWW-Authenticate": "Bearer"}
            )
            
        # Check if the Authorization header has the right format
        if not auth_header.startswith("Bearer "):
            # Log the unauthorized access attempt
            await log_unauthorized_access(
                request=request,
                reason="invalid_auth_header_format",
                additional_info={
                    "received_header": (
                        auth_header[:20] +
                        "..." if len(auth_header) > 20
                        else auth_header
                    )
                }
            )
            
            logger.warning(
                settings.textsNew.middleware
                .jwt_verification_middleware["invalid_format"]
                .format(auth_header=self.auth_header, url_path=request.url.path)
            )
            
            response = {
                "success": False,
                "statusCode": status.HTTP_401_UNAUTHORIZED,
                "message": (
                    settings.textsNew.middleware
                    .jwt_verification_middleware["invalid_format_msg"]
                )
            }
            
            # Add development information for localhost
            if self._is_localhost(request):
                response["pythonVersion"] = platform.python_version()
                response["systemVersion"] = platform.platform()
                
            # Add documentation links
            response["OpenApi-JSON-Documentation"] = f"{request.base_url}v3/api-docs"
            response["OpenApi-Documentation"] = f"{request.base_url}swagger-ui/index.html"
            
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content=response,
                headers={"WWW-Authenticate": "Bearer"}
            )
            
        # Continue processing the request
        return await call_next(request)
            
