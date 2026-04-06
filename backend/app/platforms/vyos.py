from app.platforms.base import PlatformBase

class VyOS(PlatformBase):
    name = "VyOS"
    platform_key = "vyos"
    netmiko_device_type = "vyos"
    supported_queries = {"bgp_route", "ping", "traceroute"}
