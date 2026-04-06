from app.platforms.base import PlatformBase

class Bird(PlatformBase):
    name = "BIRD"
    platform_key = "bird"
    netmiko_device_type = "linux"
    supported_queries = {"bgp_route", "bgp_community", "bgp_aspath"}
