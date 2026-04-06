from pydantic import BaseModel
from typing import List, Optional

class DeviceLocation(BaseModel):
    city: str
    country: str
    facility: Optional[str] = None
    coordinates: Optional[List[float]] = None

class DeviceNetwork(BaseModel):
    asn: int
    as_name: str

class DeviceResponse(BaseModel):
    id: str
    name: str
    platform: str
    location: DeviceLocation
    supported_queries: List[str]
    status: str = "online"
    network: DeviceNetwork

class DeviceListResponse(BaseModel):
    devices: List[DeviceResponse]
