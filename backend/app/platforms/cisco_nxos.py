from app.platforms.base import PlatformBase

class CiscoNxos(PlatformBase):
    name = "Cisco NX-OS"
    platform_key = "cisco_nxos"
    netmiko_device_type = "cisco_nxos"
    supported_queries = {"bgp_route", "bgp_community", "bgp_aspath", "ping", "traceroute"}
