import ipaddress
from ipaddress import ip_address, ip_network
from typing import List
from fastapi import Request

TRUSTED_PROXY_CIDRS: List[str] = [
    "10.0.0.0/8",
    "172.16.0.0/12",
    "192.168.0.0/16",
    "127.0.0.0/8",
    "::1/128",
]

_TRUSTED_NETWORKS = [ip_network(cidr) for cidr in TRUSTED_PROXY_CIDRS]


def _is_trusted_proxy(ip_str: str) -> bool:
    try:
        addr = ip_address(ip_str.strip())
        return any(addr in network for network in _TRUSTED_NETWORKS)
    except ValueError:
        return False


def get_client_ip(request: Request) -> str:
    """
    Resolve real client IP safely.
    Priority: X-Real-IP > X-Forwarded-For > direct connection.
    Headers are only trusted when the connecting IP is a known proxy.
    """
    connecting_ip = request.client.host if request.client else ""
    is_from_proxy = _is_trusted_proxy(connecting_ip)

    if is_from_proxy:
        x_real_ip = request.headers.get("x-real-ip")
        if x_real_ip:
            real_ip = x_real_ip.strip()
            try:
                ip_address(real_ip)
                return real_ip
            except ValueError:
                pass

    xff = request.headers.get("x-forwarded-for")
    if xff and is_from_proxy:
        ips = [ip.strip() for ip in xff.split(",")]
        for ip_str in reversed(ips):
            try:
                ip_address(ip_str)
            except ValueError:
                continue
            if not _is_trusted_proxy(ip_str):
                return ip_str

    return connecting_ip or "0.0.0.0"
