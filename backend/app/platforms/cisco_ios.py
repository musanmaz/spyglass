from app.platforms.base import PlatformBase

class CiscoIos(PlatformBase):
    name = "Cisco IOS"
    platform_key = "cisco_ios"
    netmiko_device_type = "cisco_ios"
    supported_queries = {"bgp_route", "bgp_community", "bgp_aspath", "ping", "traceroute"}
