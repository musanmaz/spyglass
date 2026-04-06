import pytest
import time
from unittest.mock import AsyncMock, MagicMock, patch
from app.api.middleware.rate_limit import RateLimitMiddleware

class TestRateLimiting:
    @pytest.fixture
    def mock_redis(self):
        redis = AsyncMock()
        pipe = AsyncMock()
        pipe.execute = AsyncMock(return_value=[None, None, 5, True])
        redis.pipeline.return_value = pipe
        redis.zrange = AsyncMock(return_value=[])
        redis.lpush = AsyncMock()
        redis.ltrim = AsyncMock()
        return redis

    @pytest.fixture
    def middleware(self, mock_redis):
        app = MagicMock()
        return RateLimitMiddleware(app, redis=mock_redis, query_limit=20, query_window=60)

    @pytest.mark.asyncio
    async def test_under_limit_passes(self, middleware, mock_redis):
        pipe = AsyncMock()
        pipe.execute = AsyncMock(return_value=[None, None, 5, True])
        mock_redis.pipeline.return_value = pipe

        allowed, remaining, retry = await middleware._check_rate_limit("rl:query:1.2.3.4", 20, 60)
        assert allowed is True
        assert remaining == 15

    @pytest.mark.asyncio
    async def test_over_limit_blocked(self, middleware, mock_redis):
        pipe = AsyncMock()
        pipe.execute = AsyncMock(return_value=[None, None, 21, True])
        mock_redis.pipeline.return_value = pipe
        mock_redis.zrange = AsyncMock(return_value=[(b"key", time.time() - 30)])

        allowed, remaining, retry = await middleware._check_rate_limit("rl:query:1.2.3.4", 20, 60)
        assert allowed is False
        assert remaining == 0
        assert retry > 0

    @pytest.mark.asyncio
    async def test_exact_limit_passes(self, middleware, mock_redis):
        pipe = AsyncMock()
        pipe.execute = AsyncMock(return_value=[None, None, 20, True])
        mock_redis.pipeline.return_value = pipe

        allowed, remaining, retry = await middleware._check_rate_limit("rl:query:1.2.3.4", 20, 60)
        assert allowed is True
        assert remaining == 0
