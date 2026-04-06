from app.platforms.base import PlatformBase

class AristaEos(PlatformBase):
    name = "Arista EOS"
    platform_key = "arista_eos"
    netmiko_device_type = "arista_eos"
    supported_queries = {"bgp_route", "bgp_community", "bgp_aspath", "ping", "traceroute"}
