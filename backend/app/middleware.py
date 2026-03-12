"""Security middleware for VotoClaro."""

import time
from collections import defaultdict

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import JSONResponse


# ---------------------------------------------------------------------------
# Security headers middleware
# ---------------------------------------------------------------------------


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add standard security headers to every response."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = (
            "camera=(), microphone=(), geolocation=()"
        )
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; frame-ancestors 'none'"
        )
        return response


# ---------------------------------------------------------------------------
# In-memory rate limiter middleware
# ---------------------------------------------------------------------------


class _RateBucket:
    """Track request timestamps for a single client."""

    __slots__ = ("timestamps",)

    def __init__(self) -> None:
        self.timestamps: list[float] = []

    def is_allowed(self, now: float, window: float, max_requests: int) -> bool:
        # Purge old entries
        self.timestamps = [t for t in self.timestamps if now - t < window]
        if len(self.timestamps) >= max_requests:
            return False
        self.timestamps.append(now)
        return True


# Paths that are rate-limited and their (window_seconds, max_requests) config
_RATE_LIMITED_PATHS: dict[str, tuple[float, int]] = {
    "/api/auth/register": (60.0, 10),       # 10 registrations per minute
    "/api/quiz/submit": (60.0, 30),         # 30 quiz submits per minute
    "/api/simulator/anti-vote": (60.0, 30), # 30 simulations per minute
    "/api/simulator/dhondt": (60.0, 30),    # 30 d'hondt calls per minute
}

_buckets: dict[str, dict[str, _RateBucket]] = defaultdict(
    lambda: defaultdict(_RateBucket)
)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple in-memory rate limiter for sensitive endpoints.

    Uses client IP as the key.  Not suitable for multi-process deployments
    without a shared store (Redis), but adequate for single-process / dev /
    moderate traffic.
    """

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        path = request.url.path.rstrip("/")
        config = _RATE_LIMITED_PATHS.get(path)

        if config is None:
            return await call_next(request)

        window, max_requests = config
        client_ip = request.client.host if request.client else "unknown"
        bucket = _buckets[path][client_ip]

        if not bucket.is_allowed(time.time(), window, max_requests):
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Demasiadas solicitudes. Intenta de nuevo en un momento."
                },
            )

        return await call_next(request)
