from fastapi import APIRouter, Depends
from typing import Dict
from app.config import settings
from app.api.deps import get_devices_config
from app.services.command_builder import CommandBuilder

router = APIRouter()


@router.get("/info")
async def app_info(devices: Dict = Depends(get_devices_config)):
    cmd_builder = CommandBuilder()
    all_queries: set[str] = set()
    for device in devices.values():
        directives = device.get("directives", [])
        if device.get("platform") == "local":
            all_queries.update(directives if directives else ["ping", "traceroute"])
        elif directives:
            platform_queries = cmd_builder.get_supported_queries(device.get("platform", ""))
            all_queries.update(q for q in platform_queries if q in directives)
        else:
            all_queries.update(cmd_builder.get_supported_queries(device.get("platform", "")))

    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "organization": settings.ORG_NAME,
        "primary_asn": settings.PRIMARY_ASN,
        "peeringdb": settings.PEERINGDB_URL,
        "website": settings.WEBSITE_URL,
        "supported_query_types": sorted(all_queries),
    }
