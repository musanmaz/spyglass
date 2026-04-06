import asyncio
import ipaddress
import socket
from typing import Optional

async def resolve_hostname(hostname: str) -> Optional[str]:
    try:
        ipaddress.ip_address(hostname)
        return hostname
    except ValueError:
        pass
    
    try:
        loop = asyncio.get_event_loop()
        result = await loop.getaddrinfo(hostname, None, family=socket.AF_UNSPEC, type=socket.SOCK_STREAM)
        if result:
            return result[0][4][0]
    except (socket.gaierror, OSError):
        pass
    return None
