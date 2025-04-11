from fastapi import Request

def is_localhost(request: Request) -> bool:
    """
    Check if the request is coming from localhost.
    """
    host = request.headers.get("host", "")
    return host.startswith("localhost:") or host.startswith("127.0.0.1:")

def is_authenticated(request: Request) -> bool:
    """
    Check if the request is authenticated.
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

def should_skip_formatting(request: Request, skip_paths: list[str]) -> bool:
    """
    Check if response formatting should be skipped for this path.
    """
    return any(request.url.path.startswith(path) for path in skip_paths)

def extract_message_from_response(body_data: Any) -> str:
    """
    Extract the actual message string from a response body that might be nested.
    """
    if isinstance(body_data, str):
        return body_data

    if isinstance(body_data, dict):
        if "message" in body_data and isinstance(body_data["message"], str):
            return body_data["message"]
        if "error" in body_data and isinstance(body_data["error"], dict) and "detail" in body_data["error"]:
            return body_data["error"]["detail"]
        if "detail" in body_data and isinstance(body_data["detail"], str):
            return body_data["detail"]

    return "An error occurred"