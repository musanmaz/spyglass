from app.platforms.base import PlatformBase

class CiscoIosxr(PlatformBase):
    name = "Cisco IOS-XR"
    platform_key = "cisco_iosxr"
    netmiko_device_type = "cisco_xr"
    supported_queries = {"bgp_route", "bgp_community", "bgp_aspath", "ping", "traceroute"}
