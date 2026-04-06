import time
import uuid
from fastapi import Request
from redis.asyncio import Redis
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from app.api.middleware.trusted_proxy import get_client_ip


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, redis: Redis, query_limit: int = 20, query_window: int = 60, general_limit: int = 60, general_window: int = 60):
        super().__init__(app)
        self.redis = redis
        self.query_limit = query_limit
        self.query_window = query_window
        self.general_limit = general_limit
        self.general_window = general_window

    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        if not path.startswith("/api/") or path == "/api/v1/health":
            return await call_next(request)

        client_ip = get_client_ip(request)

        is_query = (
            (path == "/api/v1/query" and request.method == "POST")
            or path == "/api/v1/query/stream"
        )

        if is_query:
            limit, window, key_prefix = self.query_limit, self.query_window, "rl:query"
        else:
            limit, window, key_prefix = self.general_limit, self.general_window, "rl:general"

        allowed, remaining, retry_after = await self._check_rate_limit(
            key=f"{key_prefix}:{client_ip}", limit=limit, window=window,
        )

        if not allowed:
            await self._log_rate_limit_hit(client_ip, path)
            return JSONResponse(
                status_code=429,
                content={"detail": {"error": "rate_limited", "message": f"Too many requests. Please wait {retry_after}s.", "retry_after": retry_after, "limit": limit, "window": window}},
                headers={"Retry-After": str(retry_after), "X-RateLimit-Limit": str(limit), "X-RateLimit-Remaining": "0", "X-RateLimit-Reset": str(int(time.time()) + retry_after)},
            )

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        return response

    async def _check_rate_limit(self, key: str, limit: int, window: int) -> tuple[bool, int, int]:
        """Redis sorted set sliding window. Score=timestamp, member=unique ID."""
        now = time.time()
        window_start = now - window

        pipe = self.redis.pipeline()
        pipe.zremrangebyscore(key, 0, window_start)
        pipe.zadd(key, {f"{now}:{uuid.uuid4().hex[:8]}": now})
        pipe.zcard(key)
        pipe.expire(key, window + 10)
        results = await pipe.execute()
        current_count = results[2]

        if current_count > limit:
            oldest = await self.redis.zrange(key, 0, 0, withscores=True)
            if oldest:
                retry_after = int(window - (now - oldest[0][1])) + 1
            else:
                retry_after = window
            return False, 0, max(retry_after, 1)

        return True, limit - current_count, 0

    async def _log_rate_limit_hit(self, client_ip: str, path: str):
        await self.redis.lpush("audit:rate_limits", f"{time.time()}|{client_ip}|{path}")
        await self.redis.ltrim("audit:rate_limits", 0, 9999)
