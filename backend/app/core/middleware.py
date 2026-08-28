"""
Production security, correlation, rate limiting, and observability middlewares.
"""

import time
import uuid
import logging
from collections import defaultdict
from typing import Callable, Dict
from fastapi import Request, Response, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.core.config import settings
from app.core.logging import correlation_id_ctx
from app.core.errors import create_error_response

logger = logging.getLogger("riskshield.access")


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """
    Middleware that captures or generates a unique correlation ID for every request,
    sets it in request.state, binds it to contextvars for logging, and returns it in response headers.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        correlation_id = (
            request.headers.get("X-Correlation-ID")
            or request.headers.get("X-Request-ID")
            or f"req_{uuid.uuid4().hex[:12]}"
        )

        request.state.correlation_id = correlation_id
        token = correlation_id_ctx.set(correlation_id)

        try:
            response = await call_next(request)
            response.headers["X-Correlation-ID"] = correlation_id
            return response
        finally:
            correlation_id_ctx.reset(token)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware attaching standard enterprise security headers to every response.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)

        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = "default-src 'self'; frame-ancestors 'none';"

        if settings.ENVIRONMENT == "production":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"

        return response


class RateLimiterMiddleware(BaseHTTPMiddleware):
    """
    Sliding window in-memory rate limiter per client IP.
    """

    def __init__(self, app):
        super().__init__(app)
        self.requests: Dict[str, list] = defaultdict(list)
        self.window_seconds = 60

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if not settings.RATE_LIMIT_ENABLED or settings.ENVIRONMENT == "test":
            return await call_next(request)

        # Skip rate limiting for static/docs and liveness health check
        if request.url.path in ["/health", "/api/v1/health/liveness", "/docs", "/openapi.json"]:
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        now = time.time()
        max_requests = settings.RATE_LIMIT_REQUESTS_PER_MINUTE

        self.requests[client_ip] = [
            ts for ts in self.requests[client_ip] if now - ts < self.window_seconds
        ]

        if len(self.requests[client_ip]) >= max_requests:
            correlation_id = getattr(request.state, "correlation_id", "unknown")
            logger.warning(
                f"Rate limit exceeded for IP {client_ip}. Threshold: {max_requests}/min. Correlation ID: {correlation_id}"
            )
            return create_error_response(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                code="RATE_LIMIT_EXCEEDED",
                message="Too many requests. Please retry in a few moments.",
                correlation_id=correlation_id,
            )

        self.requests[client_ip].append(now)
        return await call_next(request)


class RequestObservabilityMiddleware(BaseHTTPMiddleware):
    """
    Middleware measuring request execution time and logging structured request access info.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.perf_counter()
        correlation_id = getattr(request.state, "correlation_id", "unknown")

        try:
            response = await call_next(request)
            process_time_ms = round((time.perf_counter() - start_time) * 1000, 2)
            response.headers["X-Process-Time"] = f"{process_time_ms}ms"

            client_ip = request.client.host if request.client else "unknown"
            logger.info(
                f"{request.method} {request.url.path} -> {response.status_code} ({process_time_ms}ms)",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "duration_ms": process_time_ms,
                    "client_ip": client_ip,
                    "correlation_id": correlation_id,
                },
            )
            return response
        except Exception as exc:
            process_time_ms = round((time.perf_counter() - start_time) * 1000, 2)
            logger.error(
                f"Unhandled error processing {request.method} {request.url.path} after {process_time_ms}ms: {exc}",
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
