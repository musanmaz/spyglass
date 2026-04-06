from app.platforms.base import PlatformBase

class FRRouting(PlatformBase):
    name = "FRRouting"
    platform_key = "frrouting"
    netmiko_device_type = "linux"
    supported_queries = {"bgp_route", "bgp_community", "bgp_aspath", "ping", "traceroute"}
