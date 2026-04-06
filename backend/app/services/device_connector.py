import asyncio
import re
from typing import Dict, Optional
from netmiko import ConnectHandler
from app.core.exceptions import DeviceConnectionError, QueryTimeoutError, SecurityError
from app.services.output_parser import OutputParser
from app.config import settings

_connection_semaphores: Dict[str, asyncio.Semaphore] = {}
MAX_CONNECTIONS_PER_DEVICE = 3

_SAFE_IP = r"[0-9a-fA-F:./]+"
_SAFE_SRC = r"[0-9a-fA-F:.]+"
_SAFE_COMMUNITY = r"[0-9:.]+"
_SAFE_REGEXP = r'"[0-9_ ^$.*+?|()\\]+"'
_OPT_PARAMS = r"( (count|source|timeout|probe|repeat|detail|wait) [0-9a-fA-F:.]+)*"

ALLOWED_COMMAND_PATTERNS: Dict[str, list[str]] = {
    "cisco_xr": [
        rf"^show ip bgp {_SAFE_IP}$",
        rf"^ping (ipv6 )?{_SAFE_IP}{_OPT_PARAMS}$",
        rf"^traceroute (ipv6 )?{_SAFE_IP}{_OPT_PARAMS}$",
    ],
    "cisco_iosxr": [
        rf"^show bgp ipv[46] unicast {_SAFE_IP}$",
        rf"^show bgp ipv[46] unicast community {_SAFE_COMMUNITY}$",
        rf"^show bgp ipv[46] unicast regexp {_SAFE_REGEXP}$",
        rf"^show route ipv[46] {_SAFE_IP}$",
        rf"^ping ipv[46] {_SAFE_IP}{_OPT_PARAMS}$",
        rf"^traceroute ipv[46] {_SAFE_IP}{_OPT_PARAMS}$",
    ],
    "juniper_junos": [
        rf"^show route {_SAFE_IP}( detail)?$",
        rf"^show route community {_SAFE_COMMUNITY}( detail)?$",
        rf'^show route aspath-regex {_SAFE_REGEXP}( detail)?$',
        rf"^ping {_SAFE_IP}{_OPT_PARAMS}$",
        rf"^traceroute {_SAFE_IP}{_OPT_PARAMS}$",
    ],
    "cisco_ios": [
        rf"^show ip bgp {_SAFE_IP}$",
        rf"^show bgp ipv6 unicast {_SAFE_IP}$",
        rf"^show ip bgp community {_SAFE_COMMUNITY}$",
        rf"^show ip bgp regexp {_SAFE_REGEXP}$",
        rf"^ping (ipv6 )?{_SAFE_IP}{_OPT_PARAMS}$",
        rf"^traceroute (ipv6 )?{_SAFE_IP}{_OPT_PARAMS}$",
    ],
    "cisco_nxos": [
        rf"^show ip bgp {_SAFE_IP}$",
        rf"^show bgp ipv6 unicast {_SAFE_IP}$",
        rf"^ping6? {_SAFE_IP}{_OPT_PARAMS}$",
        rf"^traceroute6? {_SAFE_IP}{_OPT_PARAMS}$",
    ],
    "arista_eos": [
        rf"^show ip(v6)? bgp {_SAFE_IP}$",
        rf"^ping {_SAFE_IP}{_OPT_PARAMS}$",
        rf"^traceroute {_SAFE_IP}{_OPT_PARAMS}$",
    ],
    "huawei_vrp": [
        rf"^display bgp (ipv6 )?routing-table {_SAFE_IP}$",
        rf"^ping {_SAFE_IP}{_OPT_PARAMS}$",
        rf"^tracert {_SAFE_IP}{_OPT_PARAMS}$",
    ],
    "nokia_sros": [
        rf"^show router bgp routes {_SAFE_IP}$",
        rf"^ping {_SAFE_IP}{_OPT_PARAMS}$",
        rf"^traceroute {_SAFE_IP}{_OPT_PARAMS}$",
    ],
    "mikrotik": [
        rf"^/routing/bgp/",
        rf"^/ping ",
        rf"^/tool/traceroute ",
    ],
    "frrouting": [
        rf"^show (ip |bgp ipv6 )bgp {_SAFE_IP}$",
        rf"^ping6? {_SAFE_IP}{_OPT_PARAMS}$",
        rf"^traceroute6? {_SAFE_IP}{_OPT_PARAMS}$",
    ],
    "bird": [rf"^show route {_SAFE_IP}( detail)?$"],
    "openbgpd": [rf"^show ip bgp {_SAFE_IP}$"],
    "vyos": [
        rf"^show (ip |bgp ipv6 )bgp {_SAFE_IP}$",
        rf"^ping {_SAFE_IP}{_OPT_PARAMS}$",
        rf"^traceroute {_SAFE_IP}{_OPT_PARAMS}$",
    ],
    "tnsr": [
        rf"^show ip bgp {_SAFE_IP}$",
        rf"^ping {_SAFE_IP}{_OPT_PARAMS}$",
        rf"^traceroute {_SAFE_IP}{_OPT_PARAMS}$",
    ],
}


def _is_command_allowed(command: str, platform: str) -> bool:
    patterns = ALLOWED_COMMAND_PATTERNS.get(platform, [])
    return any(re.match(pattern, command) for pattern in patterns)


def _get_semaphore(device_id: str) -> asyncio.Semaphore:
    if device_id not in _connection_semaphores:
        _connection_semaphores[device_id] = asyncio.Semaphore(MAX_CONNECTIONS_PER_DEVICE)
    return _connection_semaphores[device_id]


NETMIKO_PLATFORM_MAP = {
    "cisco_xr": "cisco_xr",
    "cisco_iosxr": "cisco_xr",
    "juniper_junos": "juniper_junos",
    "cisco_ios": "cisco_ios",
    "cisco_nxos": "cisco_nxos",
    "arista_eos": "arista_eos",
    "huawei_vrp": "huawei",
    "nokia_sros": "nokia_sros",
    "mikrotik": "mikrotik_routeros",
    "frrouting": "linux",
    "bird": "linux",
    "openbgpd": "linux",
    "vyos": "vyos",
    "tnsr": "linux",
}

NETMIKO_TELNET_MAP = {
    "cisco_ios": "cisco_ios_telnet",
    "cisco_xr": "cisco_xr_telnet",
    "cisco_nxos": "cisco_nxos",
    "juniper_junos": "juniper_junos_telnet",
}


def _resolve_device_type(platform: str, protocol: str = "ssh") -> str:
    if protocol == "telnet":
        return NETMIKO_TELNET_MAP.get(platform, NETMIKO_PLATFORM_MAP.get(platform, "linux") + "_telnet")
    return NETMIKO_PLATFORM_MAP.get(platform, "linux")


async def execute_on_device(command: str, device_config: dict) -> str:
    platform = device_config["platform"]
    device_id = device_config["id"]
    
    if not _is_command_allowed(command, platform):
        raise SecurityError(f"Command not allowed: {command[:50]}")

    semaphore = _get_semaphore(device_id)
    
    async with semaphore:
        protocol = device_config.get("protocol", "ssh")
        netmiko_params = {
            "device_type": _resolve_device_type(platform, protocol),
            "host": device_config["host"],
            "port": device_config.get("ssh", {}).get("port", 22 if protocol == "ssh" else 23),
            "username": device_config.get("username", ""),
            "password": device_config.get("password", ""),
            "timeout": device_config.get("ssh", {}).get("timeout", settings.SSH_TIMEOUT),
            "read_timeout_override": settings.SSH_COMMAND_TIMEOUT,
        }
        
        try:
            output = await asyncio.wait_for(
                asyncio.to_thread(_run_command, netmiko_params, command),
                timeout=settings.SSH_COMMAND_TIMEOUT + 5,
            )
        except asyncio.TimeoutError:
            raise QueryTimeoutError(device_id)
        except Exception:
            raise DeviceConnectionError(device_id)

    sanitized = OutputParser.sanitize(output)
    return OutputParser.truncate(sanitized)


def _run_command(params: dict, command: str) -> str:
    """Blocking Netmiko call — runs in thread pool."""
    with ConnectHandler(**params) as conn:
        return conn.send_command(command)
