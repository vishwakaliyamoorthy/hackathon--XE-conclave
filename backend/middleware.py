# Middleware and error handling
import logging
import time
import uuid
import json
from typing import Callable
from datetime import datetime

from fastapi import Request, Response, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class RequestIdMiddleware(BaseHTTPMiddleware):
    """Middleware to add request ID to all requests."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Add request ID and timestamp."""
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        
        # Store in request state
        request.state.request_id = request_id
        request.state.start_time = time.time()

        # Add to logger context
        logger.info(
            f"Request started: {request.method} {request.url.path}",
            extra={"request_id": request_id, "method": request.method, "path": request.url.path}
        )

        response = await call_next(request)
        
        # Add request ID to response
        response.headers["X-Request-ID"] = request_id
        
        # Log request completion
        process_time = time.time() - request.state.start_time
        logger.info(
            f"Request completed: {response.status_code} in {process_time:.3f}s",
            extra={"request_id": request_id, "status_code": response.status_code, "duration_ms": process_time * 1000}
        )

        return response


class ExceptionMiddleware(BaseHTTPMiddleware):
    """Middleware for handling exceptions."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Handle exceptions and return proper error responses."""
        try:
            response = await call_next(request)
            return response

        except HTTPException as exc:
            # FastAPI HTTP exceptions
            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "error": exc.detail,
                    "status_code": exc.status_code,
                    "request_id": getattr(request.state, "request_id", None),
                    "timestamp": datetime.utcnow().isoformat(),
                },
            )

        except ValueError as exc:
            # Validation errors
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "error": str(exc),
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "request_id": getattr(request.state, "request_id", None),
                    "timestamp": datetime.utcnow().isoformat(),
                },
            )

        except Exception as exc:
            # Unexpected errors
            logger.error(
                f"Unexpected error: {exc}",
                exc_info=True,
                extra={"request_id": getattr(request.state, "request_id", None)}
            )

            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "error": "Internal server error" if settings.is_production else str(exc),
                    "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "request_id": getattr(request.state, "request_id", None),
                    "timestamp": datetime.utcnow().isoformat(),
                },
            )


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for structured logging."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Log request and response."""
        response = await call_next(request)
        
        # Structure log data
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "request_id": getattr(request.state, "request_id", None),
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": (time.time() - request.state.start_time) * 1000,
        }

        if settings.LOG_FORMAT == "json":
            logger.info(json.dumps(log_data))
        else:
            logger.info(f"{log_data['method']} {log_data['path']} {log_data['status_code']}")

        return response


class CORSMiddleware(BaseHTTPMiddleware):
    """Custom CORS middleware."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Handle CORS headers."""
        # Handle preflight requests
        if request.method == "OPTIONS":
            return Response(
                headers={
                    "Access-Control-Allow-Origin": ", ".join(settings.CORS_ORIGINS),
                    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, PATCH",
                    "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Request-ID",
                    "Access-Control-Max-Age": "3600",
                }
            )

        response = await call_next(request)

        # Add CORS headers to response
        response.headers["Access-Control-Allow-Origin"] = ", ".join(settings.CORS_ORIGINS)
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Request-ID"

        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Basic rate limiting middleware."""

    def __init__(self, app, requests_per_minute: int = 100):
        """Initialize rate limiter."""
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests: dict = {}  # ip -> [timestamps]

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Check rate limits."""
        client_ip = request.client.host if request.client else "unknown"
        
        now = time.time()
        minute_ago = now - 60

        # Clean up old requests
        if client_ip in self.requests:
            self.requests[client_ip] = [
                req_time for req_time in self.requests[client_ip]
                if req_time > minute_ago
            ]
        else:
            self.requests[client_ip] = []

        # Check rate limit
        if len(self.requests[client_ip]) >= self.requests_per_minute:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "Rate limit exceeded",
                    "requests_per_minute": self.requests_per_minute,
                },
            )

        # Record request
        self.requests[client_ip].append(now)

        response = await call_next(request)
        
        # Add rate limit headers
        remaining = self.requests_per_minute - len(self.requests[client_ip])
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(max(0, remaining))

        return response
