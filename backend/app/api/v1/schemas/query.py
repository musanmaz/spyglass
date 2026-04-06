import re
from pydantic import BaseModel, field_validator, model_validator
from typing import List, Optional
from app.core.constants import SUPPORTED_QUERY_TYPES
from app.core.security import validate_ip_or_prefix, _check_forbidden_patterns
from app.core.exceptions import LookingGlassError


class QueryRequest(BaseModel):
    query_type: str
    target: str
    device_ids: Optional[List[str]] = None

    @field_validator("query_type")
    @classmethod
    def validate_query_type(cls, v: str) -> str:
        v = v.strip().lower()
        if v not in SUPPORTED_QUERY_TYPES:
            raise ValueError(f"Invalid query type. Allowed: {SUPPORTED_QUERY_TYPES}")
        return v

    @field_validator("target")
    @classmethod
    def validate_target_basic(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Target address cannot be empty")
        if len(v) > 255:
            raise ValueError("Target address is too long")
        try:
            _check_forbidden_patterns(v)
        except LookingGlassError as e:
            raise ValueError(e.message)
        return v

    @model_validator(mode="after")
    def validate_target_by_type(self) -> "QueryRequest":
        try:
            if self.query_type in ("bgp_route", "ping", "traceroute"):
                self.target = validate_ip_or_prefix(self.target)
        except LookingGlassError as e:
            raise ValueError(e.message)
        return self

    @field_validator("device_ids")
    @classmethod
    def validate_device_ids(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        if v is None:
            return v
        if len(v) > 5:
            raise ValueError("Maximum 5 devices per query")
        for device_id in v:
            if not re.match(r"^[a-z0-9\-]+$", device_id):
                raise ValueError(f"Invalid device ID format: {device_id}")
        return v

class QueryResultItem(BaseModel):
    device_id: str
    device_name: str
    platform: str
    location: dict
    network: dict
    status: str
    response_time_ms: int
    query_type: str
    target: str
    output: str
    cached: bool = False
    error: Optional[str] = None

class QueryResponse(BaseModel):
    request_id: str
    cached: bool
    timestamp: str
    results: List[QueryResultItem]
