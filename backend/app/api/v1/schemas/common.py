from pydantic import BaseModel
from typing import Optional

class ErrorDetail(BaseModel):
    error: str
    message: str
    field: Optional[str] = None
    retry_after: Optional[int] = None
    limit: Optional[int] = None
    window: Optional[int] = None
    device_id: Optional[str] = None
    target: Optional[str] = None

class ErrorResponse(BaseModel):
    detail: ErrorDetail
