from fastapi import Request, status
from fastapi.responses import JSONResponse

import platform

def generate_unauthorized_response(
    message: str, 
    request: Request, 
    reason: str, 
    additional_info: dict = None
) -> JSONResponse:
    """
    Generate a standardized error response for JWT verification failures.

    Args:
        request: The incoming request object.
        status_code: The HTTP status code for the response.
        message: The error message to include in the response.
        reason: The reason for the error (used for logging).
        additional_info: Additional information to log or include in the response.

    Returns:
        JSONResponse: The generated error response.
    """
    # Log the unauthorized access attempt
    response = {
        "success": False,
        "statusCode": status.HTTP_401_UNAUTHORIZED,
        "message": message,
    }

    # Add development information for localhost
    if request.headers.get("host", "").startswith("localhost"):
        response["pythonVersion"] = platform.python_version()
        response["systemVersion"] = platform.platform()

    # Add documentation links
    response["OpenApi-JSON-Documentation"] = f"{request.base_url}v3/api-docs"
    response["OpenApi-Documentation"] = f"{request.base_url}swagger-ui/index.html"

    # Include additional information if provided
    if additional_info:
        response["additional_info"] = additional_info

    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content=response,
        headers={"WWW-Authenticate": "Bearer"}
    )