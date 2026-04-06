from app.platforms.base import PlatformBase

class Mikrotik(PlatformBase):
    name = "MikroTik"
    platform_key = "mikrotik"
    netmiko_device_type = "mikrotik_routeros"
    supported_queries = {"bgp_route", "ping", "traceroute"}
