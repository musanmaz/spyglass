from fastapi import APIRouter, Depends
from app.api.v1.schemas.device import DeviceListResponse, DeviceResponse, DeviceLocation, DeviceNetwork
from app.api.deps import get_devices_config
from app.services.command_builder import CommandBuilder
from typing import Dict

router = APIRouter()


def _device_supported_queries(cmd_builder: CommandBuilder, device: dict) -> list[str]:
    platform_queries = cmd_builder.get_supported_queries(device.get("platform", ""))
    directives = device.get("directives", [])
    if directives:
        return [q for q in platform_queries if q in directives]
    return platform_queries


@router.get("/devices", response_model=DeviceListResponse)
async def list_devices(devices: Dict = Depends(get_devices_config)):
    cmd_builder = CommandBuilder()
    device_list = []
    for device_id, device in devices.items():
        loc = device.get("location", {})
        net = device.get("network", {})
        device_list.append(DeviceResponse(
            id=device_id,
            name=device.get("name", device_id),
            platform=device.get("platform", ""),
            location=DeviceLocation(
                city=loc.get("city", ""),
                country=loc.get("country", ""),
                facility=loc.get("facility"),
                coordinates=loc.get("coordinates"),
            ),
            supported_queries=_device_supported_queries(cmd_builder, device),
            status="online",
            network=DeviceNetwork(
                asn=net.get("asn", 0),
                as_name=net.get("as_name", ""),
            ),
        ))
    return DeviceListResponse(devices=device_list)
