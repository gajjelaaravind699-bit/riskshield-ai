"""
Centralized safe error handling and sensitive detail sanitization.
"""

import logging
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings

logger = logging.getLogger("riskshield.errors")


def create_error_response(
    status_code: int,
    code: str,
    message: str,
    correlation_id: str,
    details: Optional[Any] = None,
) -> JSONResponse:
    """
    Construct standardized and safe JSON error response.
    Includes both 'detail' (for standard FastAPI clients) and structured 'error' envelope.
    """
    payload: Dict[str, Any] = {
        "detail": message,
        "error": {
            "code": code,
            "message": message,
            "correlation_id": correlation_id,
        },
    }
    if details is not None:
        payload["error"]["details"] = details

    return JSONResponse(
        status_code=status_code,
        content=payload,
        headers={"X-Correlation-ID": correlation_id},
    )


def register_exception_handlers(app: FastAPI) -> None:
    """
    Register global exception handlers on the FastAPI application instance.
    """

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        correlation_id = getattr(request.state, "correlation_id", "unknown")
        
        detail_msg = exc.detail if isinstance(exc.detail, str) else str(exc.detail)
        code = f"HTTP_{exc.status_code}"
        if exc.status_code == status.HTTP_401_UNAUTHORIZED:
            code = "UNAUTHORIZED"
        elif exc.status_code == status.HTTP_403_FORBIDDEN:
            code = "FORBIDDEN"
        elif exc.status_code == status.HTTP_404_NOT_FOUND:
            code = "NOT_FOUND"

        return create_error_response(
            status_code=exc.status_code,
            code=code,
            message=detail_msg,
            correlation_id=correlation_id,
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        correlation_id = getattr(request.state, "correlation_id", "unknown")
        
        sanitized_errors: List[Dict[str, Any]] = []
        for err in exc.errors():
            loc = [str(part) for part in err.get("loc", []) if part != "body"]
            sanitized_errors.append({
                "field": ".".join(loc) if loc else "body",
                "message": err.get("msg", "Invalid input value"),
            })

        return create_error_response(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            code="VALIDATION_ERROR",
            message="Request validation failed. Please check the supplied input.",
            correlation_id=correlation_id,
            details=sanitized_errors,
        )

    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
        correlation_id = getattr(request.state, "correlation_id", "unknown")
        logger.error(
            f"Database error during {request.method} {request.url.path}: {exc}",
            exc_info=True,
            extra={"correlation_id": correlation_id},
        )

        message = (
            "A database error occurred while processing your request. "
            f"Please contact support with Correlation ID: {correlation_id}"
        )
        if settings.ENVIRONMENT != "production" and settings.DEBUG:
            message = f"Database error: {str(exc)}"

        return create_error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            code="DATABASE_ERROR",
            message=message,
            correlation_id=correlation_id,
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        correlation_id = getattr(request.state, "correlation_id", "unknown")
        logger.critical(
            f"Unhandled exception during {request.method} {request.url.path}: {exc}",
            exc_info=True,
            extra={"correlation_id": correlation_id},
        )

        message = (
            "An unexpected internal error occurred. "
            f"Please reference Correlation ID: {correlation_id}"
        )
        if settings.ENVIRONMENT == "development" and settings.DEBUG:
            message = f"Internal error: {str(exc)}"

        return create_error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            code="INTERNAL_SERVER_ERROR",
            message=message,
            correlation_id=correlation_id,
        )
