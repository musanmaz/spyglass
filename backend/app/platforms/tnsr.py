from app.platforms.base import PlatformBase

class Tnsr(PlatformBase):
    name = "TNSR"
    platform_key = "tnsr"
    netmiko_device_type = "linux"
    supported_queries = {"bgp_route", "ping", "traceroute"}
