import structlog
from fastapi import status
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded

logger = structlog.get_logger()


class StarterBaseException(Exception):
    """Base exception class for all system error"""

    def __init__(self, message: str, code: str = "INTERNAL_ERROR") -> None:
        self.message = message
        self.code = code
        super().__init__(message)


class NotFoundError(StarterBaseException):
    """Resource not found"""

    def __init__(self, resource: str, identifier: str | int) -> None:
        self.resource = resource
        self.identifier = identifier
        super().__init__(message=f"{resource} not found", code="NOT_FOUND")


class AuthenticationError(StarterBaseException):
    """Authentication failed"""

    def __init__(self, message: str = "Authentication failed") -> None:
        super().__init__(message, code="AUTH_FAILED")


class AuthorizationError(StarterBaseException):
    """Authorization failed"""

    def __init__(self, message: str = "Permission denied") -> None:
        super().__init__(message, code="FORBIDDEN")


class ValidationError(StarterBaseException):
    """Validation Error"""

    def __init__(self, message: str) -> None:
        super().__init__(message, code="VALIDATION_ERROR")


# === Status Code Mapping ===
STATUS_MAP = {
    # Auth
    "AUTH_FAILED": status.HTTP_401_UNAUTHORIZED,
    "INVALID_CREDENTIALS_OR_USER_DISABLED": status.HTTP_401_UNAUTHORIZED,
    "FORBIDDEN": status.HTTP_403_FORBIDDEN,
    # Resource
    "NOT_FOUND": status.HTTP_404_NOT_FOUND,
    "USER_NOT_FOUND": status.HTTP_404_NOT_FOUND,
    # Conflict
    "EMAIL_EXISTS": status.HTTP_409_CONFLICT,
    # Validation
    "VALIDATION_ERROR": status.HTTP_422_UNPROCESSABLE_CONTENT,
    # Others
    # ...
}


async def starter_exception_handler(
    request: Request, exc: StarterBaseException
) -> JSONResponse:
    """Handle custom exceptions"""
    log_kwargs: dict = {
        "code": exc.code,
        "message": exc.message,
        "path": request.url.path,
    }
    if isinstance(exc, NotFoundError):
        log_kwargs["resource"] = exc.resource
        log_kwargs["identifier"] = exc.identifier
    logger.warning("starter_exception", **log_kwargs)

    return JSONResponse(
        content={"error": {"code": exc.code, "message": exc.message}},
        status_code=STATUS_MAP.get(exc.code, status.HTTP_500_INTERNAL_SERVER_ERROR),
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle uncaught exception"""

    logger.exception("unhandled_exception", error=str(exc), path=request.url.path)

    return JSONResponse(
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
            }
        },
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


async def rate_limit_exceeded_handler(
    request: Request, exc: RateLimitExceeded
) -> JSONResponse:
    """Custom exception handler to avoid default from
    from slowapi import _rate_limit_exceeded_handler
    that expose message like "Rate limit exceeded: 5 per 1 minute".

    Using this custom handler does not expose any info
    """
    logger.warning("rate_limit_exceeded", path=request.url.path)
    return JSONResponse(
        content={
            "error": {"code": "TOO_MANY_REQUESTS", "message": "Too many requests"}
        },
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
    )
