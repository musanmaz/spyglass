import hmac
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse


class ApiTokenMiddleware(BaseHTTPMiddleware):
    """Rejects all /api/ requests that don't carry a valid proxy token."""

    EXEMPT_PATHS = {"/api/v1/health"}

    def __init__(self, app, token: str, require: bool = True):
        super().__init__(app)
        self.token = token
        self.require = require

    async def dispatch(self, request: Request, call_next):
        if not self.require:
            return await call_next(request)

        path = request.url.path

        if not path.startswith("/api/"):
            return await call_next(request)

        if path in self.EXEMPT_PATHS:
            return await call_next(request)

        incoming = request.headers.get("X-API-Token", "")
        if not hmac.compare_digest(incoming, self.token):
            return JSONResponse(
                status_code=403,
                content={"detail": "Forbidden"},
            )

        return await call_next(request)
