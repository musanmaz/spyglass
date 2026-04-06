from fastapi import APIRouter, Depends
from redis.asyncio import Redis
from app.api.deps import get_redis, get_devices_config
import time

router = APIRouter()
_start_time = time.time()


@router.get("/health")
async def health_check(redis: Redis = Depends(get_redis), devices: dict = Depends(get_devices_config)):
    components = {"cache": "ok"}

    try:
        await redis.ping()
    except Exception:
        components["cache"] = "error"

    components["devices_total"] = len(devices)
    components["devices_reachable"] = len(devices)

    status = "healthy" if components["cache"] == "ok" else "degraded"

    return {
        "status": status,
        "version": "1.0.0",
        "uptime": int(time.time() - _start_time),
        "components": components,
    }
