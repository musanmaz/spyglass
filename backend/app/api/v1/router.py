from fastapi import APIRouter
from app.api.v1.endpoints import query, devices, health, info, stream, myip

api_router = APIRouter()
api_router.include_router(query.router, tags=["Query"])
api_router.include_router(stream.router, tags=["Stream"])
api_router.include_router(devices.router, tags=["Devices"])
api_router.include_router(health.router, tags=["Health"])
api_router.include_router(info.router, tags=["Info"])
api_router.include_router(myip.router, tags=["MyIP"])
