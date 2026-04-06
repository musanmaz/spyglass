from app.platforms.base import PlatformBase

class HuaweiVrp(PlatformBase):
    name = "Huawei VRP"
    platform_key = "huawei_vrp"
    netmiko_device_type = "huawei"
    supported_queries = {"bgp_route", "bgp_community", "ping", "traceroute"}
