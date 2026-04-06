from typing import AsyncGenerator, Dict
from functools import lru_cache
from pathlib import Path
import yaml

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db.session import async_session_factory
from app.core.cache import CacheService
from app.services.query_executor import QueryExecutor
from app.services.acl_checker import AclChecker
from app.services.command_builder import CommandBuilder

_redis_client: Redis | None = None
_devices_cache: Dict[str, dict] | None = None


def get_redis() -> Redis:
    global _redis_client
    if _redis_client is None:
        _redis_client = Redis.from_url(settings.REDIS_URL, decode_responses=True)
    return _redis_client


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


@lru_cache()
def get_devices_config() -> Dict[str, dict]:
    global _devices_cache
    if _devices_cache is not None:
        return _devices_cache
    path = Path(settings.DEVICES_CONFIG_PATH)
    if not path.exists():
        return {}
    with open(path) as f:
        data = yaml.safe_load(f)
    devices = {}
    for d in data.get("devices", []):
        if settings.DEVICE_SSH_USERNAME:
            d["username"] = settings.DEVICE_SSH_USERNAME
        if settings.DEVICE_SSH_PASSWORD:
            d["password"] = settings.DEVICE_SSH_PASSWORD
        devices[d["id"]] = d
    _devices_cache = devices
    return _devices_cache


@lru_cache()
def _get_acl_checker() -> AclChecker:
    return AclChecker(settings.ACL_CONFIG_PATH)


@lru_cache()
def _get_command_builder() -> CommandBuilder:
    return CommandBuilder(settings.COMMANDS_CONFIG_PATH)


def get_query_executor() -> QueryExecutor:
    redis = get_redis()
    cache = CacheService(redis, default_ttl=settings.CACHE_TTL)
    devices = get_devices_config()
    return QueryExecutor(
        cache=cache,
        devices=devices,
        acl_checker=_get_acl_checker(),
        command_builder=_get_command_builder(),
    )
