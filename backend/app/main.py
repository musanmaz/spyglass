from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.config import settings
from app.core.logging import setup_logging
from app.api.middleware.security_headers import SecurityHeadersMiddleware
from app.api.middleware.rate_limit import RateLimitMiddleware
from app.api.middleware.request_id import RequestIdMiddleware
from app.api.middleware.logging import AccessLogMiddleware
from app.api.middleware.api_token import ApiTokenMiddleware
from app.api.middleware.cookie_session import CookieSessionMiddleware
from app.api.middleware.cors import setup_cors
from app.api.deps import get_redis


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging("DEBUG" if settings.ENVIRONMENT == "development" else "INFO")
    yield
    redis = get_redis()
    await redis.close()


def create_app() -> FastAPI:
    if settings.ENVIRONMENT == "production":
        if "change-me" in settings.API_PROXY_TOKEN:
            raise RuntimeError("FATAL: API_PROXY_TOKEN must be changed from default before running in production")
        if "change-me" in settings.SECRET_KEY:
            raise RuntimeError("FATAL: SECRET_KEY must be changed from default before running in production")

    application = FastAPI(
        title=f"{settings.APP_NAME} API",
        version=settings.APP_VERSION,
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
        lifespan=lifespan,
    )

    application.add_middleware(SecurityHeadersMiddleware)
    application.add_middleware(
        CookieSessionMiddleware,
        secret=settings.SECRET_KEY,
        redis=get_redis(),
        ttl=settings.SESSION_TOKEN_TTL,
        max_uses=settings.SESSION_TOKEN_MAX_USES,
    )
    application.add_middleware(
        ApiTokenMiddleware,
        token=settings.API_PROXY_TOKEN,
    )
    application.add_middleware(
        RateLimitMiddleware,
        redis=get_redis(),
        query_limit=settings.RATE_LIMIT_QUERY,
        query_window=settings.RATE_LIMIT_QUERY_WINDOW,
        general_limit=settings.RATE_LIMIT_GENERAL,
        general_window=settings.RATE_LIMIT_GENERAL_WINDOW,
    )
    application.add_middleware(RequestIdMiddleware)
    application.add_middleware(AccessLogMiddleware)
    if settings.CORS_ORIGINS:
        setup_cors(application)

    from app.api.v1.router import api_router
    from app.api.v1.endpoints.ws_query import router as ws_router
    application.include_router(api_router, prefix="/api/v1")
    application.include_router(ws_router)

    @application.exception_handler(ValidationError)
    async def validation_exception_handler(request, exc):
        errors = exc.errors()
        first = errors[0] if errors else {}
        return JSONResponse(
            status_code=422,
            content={"detail": {"error": "validation_error", "message": first.get("msg", "Validation error"), "field": str(first.get("loc", [""])[-1])}},
        )

    return application


app = create_app()
