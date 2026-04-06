import ipaddress
import re
from typing import Optional

def is_valid_ipv4(value: str) -> bool:
    try:
        addr = ipaddress.IPv4Address(value)
        return True
    except (ipaddress.AddressValueError, ValueError):
        return False

def is_valid_ipv6(value: str) -> bool:
    try:
        addr = ipaddress.IPv6Address(value)
        return True
    except (ipaddress.AddressValueError, ValueError):
        return False

def is_valid_prefix(value: str) -> bool:
    try:
        ipaddress.ip_network(value, strict=False)
        return True
    except ValueError:
        return False

def get_ip_version(target: str) -> int:
    addr_str = target.split("/")[0]
    try:
        addr = ipaddress.ip_address(addr_str)
        return addr.version
    except ValueError:
        return 4

def is_valid_community(value: str) -> bool:
    if re.match(r"^\d{1,5}:\d{1,5}$", value):
        return True
    if re.match(r"^\d{1,10}:\d{1,10}:\d{1,10}$", value):
        return True
    return False

def is_valid_aspath_regex(value: str) -> bool:
    if not re.match(r'^[\d\s\^$_.*+?\[\](){}|]+$', value):
        return False
    if len(value) > 128:
        return False
    return True
