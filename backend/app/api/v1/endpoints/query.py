from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from app.api.v1.schemas.query import QueryRequest, QueryResponse
from app.api.deps import get_query_executor, get_devices_config
from app.services.query_executor import QueryExecutor
from app.core.exceptions import LookingGlassError, TargetDeniedError, DeviceNotFoundError, QueryTimeoutError, SecurityError
from app.core.logging import get_logger
from app.config import settings

router = APIRouter()
logger = get_logger("api.query")


@router.post("/query", response_model=QueryResponse)
async def execute_query(
    body: QueryRequest,
    request: Request,
    executor: QueryExecutor = Depends(get_query_executor),
    devices: dict = Depends(get_devices_config),
):
    device_ids = body.device_ids
    if not device_ids:
        device_ids = list(devices.keys())[:1]
    device_ids = device_ids[:settings.MAX_DEVICES_PER_QUERY]

    try:
        result = await executor.execute(
            query_type=body.query_type,
            target=body.target,
            device_ids=device_ids,
        )
        return result
    except TargetDeniedError as e:
        return JSONResponse(status_code=403, content={"detail": {"error": "target_denied", "message": e.message, "target": e.target}})
    except DeviceNotFoundError as e:
        return JSONResponse(status_code=404, content={"detail": {"error": "device_not_found", "message": e.message, "device_id": e.device_id}})
    except QueryTimeoutError as e:
        return JSONResponse(status_code=408, content={"detail": {"error": "query_timeout", "message": e.message, "device_id": e.device_id}})
    except SecurityError as e:
        return JSONResponse(status_code=403, content={"detail": {"error": "security_violation", "message": e.message}})
    except LookingGlassError as e:
        return JSONResponse(status_code=e.status_code, content={"detail": {"error": "query_error", "message": e.message}})
