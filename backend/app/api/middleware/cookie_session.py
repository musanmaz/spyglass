import hashlib
import hmac
import secrets
import time

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.api.middleware.trusted_proxy import get_client_ip

COOKIE_NAME = "lg_sid"
REDIS_PREFIX = "csess:"


class CookieSessionMiddleware(BaseHTTPMiddleware):
    """
    Two-layer protection using HttpOnly cookies + Origin/Referer check.

    Non-query endpoints: auto-create session cookie if missing.
    Query endpoints: REQUIRE valid cookie AND browser Origin/Referer header.
    """

    QUERY_PREFIXES = ("/api/v1/query",)
    EXEMPT_PATHS = {"/api/v1/health"}

    def __init__(self, app, secret: str, redis, ttl: int = 600, max_uses: int = 50):
        super().__init__(app)
        self.secret = secret
        self.redis = redis
        self.ttl = ttl
        self.max_uses = max_uses

    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        if not path.startswith("/api/") or path in self.EXEMPT_PATHS:
            return await call_next(request)

        client_ip = get_client_ip(request)
        cookie = request.cookies.get(COOKIE_NAME)
        is_query = any(path.startswith(p) for p in self.QUERY_PREFIXES)

        if is_query:
            if not cookie:
                return JSONResponse(status_code=403, content={"detail": "Forbidden"})
            if not await self._validate(cookie, client_ip):
                return JSONResponse(status_code=403, content={"detail": "Forbidden"})
            if not self._check_browser(request):
                return JSONResponse(status_code=403, content={"detail": "Forbidden"})
            return await call_next(request)

        response = await call_next(request)

        if not cookie or not await self._validate(cookie, client_ip):
            if not await self._is_rate_limited(client_ip):
                new_cookie = await self._create(client_ip)
                if new_cookie:
                    response.set_cookie(
                        COOKIE_NAME,
                        new_cookie,
                        httponly=True,
                        samesite="strict",
                        path="/api",
                        max_age=self.ttl,
                    )

        return response

    def _sign(self, token: str, ip: str) -> str:
        return hmac.new(
            self.secret.encode(),
            f"{token}:{ip}".encode(),
            hashlib.sha256,
        ).hexdigest()[:24]

    async def _create(self, client_ip: str) -> str | None:
        token = secrets.token_urlsafe(24)
        sig = self._sign(token, client_ip)
        cookie_val = f"{token}.{sig}"

        key = f"{REDIS_PREFIX}{token}"
        await self.redis.hset(key, mapping={
            "ip": client_ip,
            "ts": str(int(time.time())),
            "n": "0",
        })
        await self.redis.expire(key, self.ttl)
        return cookie_val

    async def _validate(self, cookie: str, client_ip: str) -> bool:
        if "." not in cookie:
            return False

        token, sig = cookie.rsplit(".", 1)
        expected = self._sign(token, client_ip)
        if not hmac.compare_digest(sig, expected):
            return False

        key = f"{REDIS_PREFIX}{token}"
        data = await self.redis.hgetall(key)
        if not data:
            return False
        if data.get("ip") != client_ip:
            return False

        uses = int(data.get("n", "0"))
        if uses >= self.max_uses:
            await self.redis.delete(key)
            return False

        await self.redis.hincrby(key, "n", 1)
        return True

    async def _is_rate_limited(self, client_ip: str) -> bool:
        rate_key = f"{REDIS_PREFIX}rl:{client_ip}"
        count = await self.redis.incr(rate_key)
        if count == 1:
            await self.redis.expire(rate_key, 60)
        return count > 10

    @staticmethod
    def _check_browser(request: Request) -> bool:
        sec_fetch_site = request.headers.get("sec-fetch-site", "")
        sec_fetch_mode = request.headers.get("sec-fetch-mode", "")

        if sec_fetch_site == "same-origin":
            return True

        if not sec_fetch_site:
            origin = request.headers.get("origin", "")
            referer = request.headers.get("referer", "")
            return bool(origin and referer)

        return False
