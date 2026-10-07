import time

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware


class RateLimitMiddleware(BaseHTTPMiddleware):

    def __init__(
        self,
        app,
        requests_limit: int = 60,
        window_seconds: int = 60,
        auth_requests_limit: int = 5,
        auth_window_seconds: int = 60
    ):
        super().__init__(app)

        self.requests_limit = requests_limit
        self.window_seconds = window_seconds

        self.auth_requests_limit = auth_requests_limit
        self.auth_window_seconds = auth_window_seconds

        # Stores:
        # (IP address, request type) -> (window start time, request count)
        self.requests = {}

        self.auth_paths = {
            "/auth/login",
            "/auth/register"
        }

        self.public_paths = {
            "/",
            "/docs",
            "/openapi.json",
            "/redoc"
        }

    async def dispatch(self, request: Request, call_next):

        path = request.url.path

        # Don't rate-limit documentation/public informational endpoints
        if path in self.public_paths:
            return await call_next(request)

        # Get client IP
        if request.client:
            client_ip = request.client.host
        else:
            client_ip = "unknown"

        # Use a separate rate-limit bucket for authentication
        if path in self.auth_paths:
            bucket = "auth"
            limit = self.auth_requests_limit
            window = self.auth_window_seconds
        else:
            bucket = "general"
            limit = self.requests_limit
            window = self.window_seconds

        key = (client_ip, bucket)

        now = time.monotonic()

        window_start, request_count = self.requests.get(
            key,
            (now, 0)
        )

        # Reset the window if it has expired
        if now - window_start >= window:
            window_start = now
            request_count = 0

        # Check rate limit
        if request_count >= limit:

            retry_after = max(
                1,
                int(window - (now - window_start))
            )

            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Too many requests. Please try again later."
                },
                headers={
                    "Retry-After": str(retry_after)
                }
            )

        # Increase request count
        self.requests[key] = (
            window_start,
            request_count + 1
        )

        return await call_next(request)