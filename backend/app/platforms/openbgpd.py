from app.platforms.base import PlatformBase

class OpenBgpd(PlatformBase):
    name = "OpenBGPD"
    platform_key = "openbgpd"
    netmiko_device_type = "linux"
    supported_queries = {"bgp_route", "bgp_community", "bgp_aspath"}
