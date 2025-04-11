from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse, Response
from starlette.requests import Request
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.exceptions import HTTPException as FastAPIHTTPException
from starlette.types import ASGIApp
from src.base.services.consumer_info import ConsumerInfoService
import json
import platform
import sys
import socket
from typing import Dict, Any, Optional, Union

class ResponseFormatMiddleware(BaseHTTPMiddleware):
    """
    Middleware to standardize the format of API responses.
    Includes consumer information for authenticated requests.
    """

    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)
        self.consumer_info_service = ConsumerInfoService()
        self.skip_paths = [
            "/docs",
            "/redoc",
            "/openapi.json",
            "/swagger-ui/index.html",
            "/v3/api-docs"
        ]

    def _should_skip_formatting(self, request: Request) -> bool:
        """
        Check if response formatting should be skipped for this path.
        
        Args:
            request: The FastAPI request object
            
        Returns:
            bool: True if formatting should be skipped
        """
        return any(request.url.path.startswith(path) for path in self.skip_paths)

    def _is_authenticated(self, request: Request) -> bool:
        """
        Check if the request is authenticated.
        
        Args:
            request: The FastAPI request object
            
        Returns:
            bool: True if the request is authenticated
        """
        # Check for API key in headers
        api_key = request.headers.get("X-API-Key")
        if api_key:
            return True
            
        # Check for Bearer token
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
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
        
    def _extract_message_from_response(self, body_data: Any) -> str:
        """
        Extract the actual message string from a response body that might be nested.
        
        Args:
            body_data: The response body data that might contain a nested message
            
        Returns:
            str: The extracted message string
        """
        # If body_data is a string, use it directly
        if isinstance(body_data, str):
            return body_data
            
        # If body_data is a dict, extract the message
        if isinstance(body_data, dict):
            # If there's a direct message field, use it
            if "message" in body_data and isinstance(body_data["message"], str):
                return body_data["message"]
                
            # If there's an error.detail field (common in FastAPI), use it
            if "error" in body_data and isinstance(body_data["error"], dict) and "detail" in body_data["error"]:
                return body_data["error"]["detail"]
                
            # If there's a detail field directly, use it
            if "detail" in body_data and isinstance(body_data["detail"], str):
                return body_data["detail"]
                
        # Default message if we can't extract one
        return "An error occurred"

    async def dispatch(self, request: Request, call_next):
        try:
            # Process the request and get the response
            response = await call_next(request)

            # Skip formatting for documentation endpoints
            if self._should_skip_formatting(request):
                return response

            print(f"Response: {response}")
            
        except (StarletteHTTPException, FastAPIHTTPException) as exc:
            # If an HTTPException is raised, handle it separately
            standardized_response = {
                "success": False,
                "statusCode": exc.status_code,
                "message": exc.detail
            }
            
            # Add consumer information if authenticated
            if self._is_authenticated(request):
                consumer_info = self.consumer_info_service.get_active_consumer_info()
                if consumer_info:
                    standardized_response["consumerInformation"] = consumer_info
                    
            # Add development information if localhost
            if self._is_localhost(request):
                standardized_response["pythonVersion"] = platform.python_version()
                standardized_response["systemVersion"] = platform.platform()
                
            return JSONResponse(content=standardized_response, status_code=exc.status_code)
        except Exception as exc:
            # Handle any unexpected exceptions
            standardized_response = {
                "success": False,
                "statusCode": 500,
                "message": "An unexpected error occurred."
            }
            
            # Add detailed error in development
            if self._is_localhost(request):
                standardized_response["pythonVersion"] = platform.python_version()
                standardized_response["systemVersion"] = platform.platform()
                standardized_response["error"] = str(exc)
                
            return JSONResponse(content=standardized_response, status_code=500)

        # Check if the response is a StreamingResponse or does not contain a body
        if isinstance(response, Response) and hasattr(response, "body_iterator"):
            # Read the response body
            body = b"".join([chunk async for chunk in response.body_iterator])
            response.body_iterator = iter([body])  # Set the body iterator back

            # Load the response body as JSON if applicable
            try:
                body_data = json.loads(body.decode("utf-8"))
            except (json.JSONDecodeError, UnicodeDecodeError):
                body_data = None
        else:
            # For other response types, retrieve the body directly
            body_data = getattr(response, "body", None)
            if body_data:
                try:
                    body_data = json.loads(body_data)
                except (json.JSONDecodeError, UnicodeDecodeError):
                    pass
        
        # Standardize the response format
        standardized_response = {
            "success": response.status_code < 400,
            "statusCode": response.status_code
        }
        
        # Add data for successful responses
        if response.status_code < 400:
            if body_data:
                standardized_response["data"] = body_data
            standardized_response["message"] = "Operation completed successfully"
        # Add error message for error responses
        else:
            if response.status_code >= 400:
                if body_data:
                    # Extract the message from the response body
                    standardized_response["message"] = self._extract_message_from_response(body_data)
                    
                    # If there's data in the error response, include it
                    if isinstance(body_data, dict) and "data" in body_data and body_data["data"] is not None:
                        standardized_response["data"] = body_data["data"]
                else:
                    standardized_response["message"] = "An error occurred"
        
        # Add consumer information for authenticated requests
        if self._is_authenticated(request):
            consumer_info = self.consumer_info_service.get_active_consumer_info()
            if consumer_info:
                standardized_response["consumerInformation"] = consumer_info
                
        # Add development information for localhost requests
        if self._is_localhost(request):
            standardized_response["pythonVersion"] = platform.python_version()
            standardized_response["systemVersion"] = platform.platform()
            
        # Add documentation links for unauthenticated responses
        if not self._is_authenticated(request):
            standardized_response["OpenApi-JSON-Documentation"] = f"{request.base_url}v3/api-docs"
            standardized_response["OpenApi-Documentation"] = f"{request.base_url}swagger-ui/index.html"

        # Return the new formatted JSON response
        return JSONResponse(content=standardized_response, status_code=response.status_code)