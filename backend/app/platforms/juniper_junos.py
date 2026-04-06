from app.platforms.base import PlatformBase

class JuniperJunos(PlatformBase):
    name = "Juniper Junos"
    platform_key = "juniper_junos"
    netmiko_device_type = "juniper_junos"
    supported_queries = {"bgp_route", "bgp_community", "bgp_aspath", "ping", "traceroute"}
