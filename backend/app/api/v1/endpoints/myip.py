from fastapi import APIRouter, Request
from app.api.middleware.trusted_proxy import get_client_ip

router = APIRouter()


@router.get("/myip")
async def get_my_ip(request: Request):
    client_ip = get_client_ip(request)
    return {"ip": client_ip}
