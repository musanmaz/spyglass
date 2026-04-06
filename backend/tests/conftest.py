import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def mock_redis():
    redis = AsyncMock()
    redis.get = AsyncMock(return_value=None)
    redis.set = AsyncMock()
    redis.pipeline = MagicMock()
    pipe = AsyncMock()
    pipe.execute = AsyncMock(return_value=[None, None, 1, True])
    redis.pipeline.return_value = pipe
    redis.zrange = AsyncMock(return_value=[])
    redis.lpush = AsyncMock()
    redis.ltrim = AsyncMock()
    redis.ping = AsyncMock()
    return redis

@pytest.fixture
def sample_devices():
    return {
        "test-router": {
            "id": "test-router",
            "name": "Test Router",
            "host": "10.0.0.1",
            "platform": "cisco_iosxr",
            "location": {"city": "Istanbul", "country": "TR"},
            "network": {"asn": 65000, "as_name": "Example Network", "ipv4_source": "198.51.100.1"},
            "ssh": {"port": 22, "timeout": 10},
        }
    }
