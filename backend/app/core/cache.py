import hashlib
import json
from typing import Any, Optional
from redis.asyncio import Redis


class CacheService:
    def __init__(self, redis: Redis, default_ttl: int = 120):
        self.redis = redis
        self.default_ttl = default_ttl

    def _make_key(self, query_type: str, target: str, device_id: str) -> str:
        raw = f"{query_type}:{target}:{device_id}"
        hashed = hashlib.sha256(raw.encode()).hexdigest()[:16]
        return f"cache:query:{hashed}"

    async def get(self, query_type: str, target: str, device_id: str) -> Optional[dict]:
        key = self._make_key(query_type, target, device_id)
        data = await self.redis.get(key)
        if data:
            return json.loads(data)
        return None

    async def set(self, query_type: str, target: str, device_id: str, result: dict, ttl: Optional[int] = None) -> None:
        key = self._make_key(query_type, target, device_id)
        await self.redis.set(key, json.dumps(result, default=str), ex=ttl or self.default_ttl)
