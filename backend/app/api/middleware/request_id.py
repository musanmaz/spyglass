import re
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

_VALID_REQUEST_ID = re.compile(r"^[a-zA-Z0-9_\-]{1,128}$")


class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        client_id = request.headers.get("x-request-id", "")
        if client_id and _VALID_REQUEST_ID.match(client_id):
            request_id = client_id
        else:
            request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response
