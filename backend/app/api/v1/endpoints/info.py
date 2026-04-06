from fastapi import APIRouter
from app.config import settings

router = APIRouter()


@router.get("/info")
async def app_info():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "organization": settings.ORG_NAME,
        "primary_asn": settings.PRIMARY_ASN,
        "peeringdb": settings.PEERINGDB_URL,
        "website": settings.WEBSITE_URL,
        "supported_query_types": ["bgp_route", "ping", "traceroute"],
    }
