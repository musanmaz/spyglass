from app.platforms.base import PlatformBase

class NokiaSros(PlatformBase):
    name = "Nokia SR OS"
    platform_key = "nokia_sros"
    netmiko_device_type = "nokia_sros"
    supported_queries = {"bgp_route", "bgp_community", "bgp_aspath", "ping", "traceroute"}
