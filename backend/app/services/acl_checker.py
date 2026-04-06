import ipaddress
import logging
from ipaddress import ip_address, ip_network
from pathlib import Path
from typing import List, Optional
import yaml

logger = logging.getLogger("acl_checker")


class AclChecker:
    def __init__(self, config_path: str = "config/acl.yaml"):
        self._denied_networks: List[ipaddress.IPv4Network | ipaddress.IPv6Network] = []
        self._denied_hosts: List[ipaddress.IPv4Address | ipaddress.IPv6Address] = []
        self._min_prefix: dict = {"ipv4": 8, "ipv6": 16}
        self._max_prefix: dict = {"ipv4": 32, "ipv6": 128}
        self._fail_closed = False
        self._load_config(config_path)

    def _load_config(self, config_path: str) -> None:
        path = Path(config_path)
        if not path.exists():
            logger.warning("ACL config not found at %s — defaulting to deny-all", config_path)
            self._fail_closed = True
            return
        with open(path) as f:
            data = yaml.safe_load(f)
        acl = data.get("acl", {})
        for prefix in acl.get("denied_prefixes", []):
            try:
                self._denied_networks.append(ip_network(prefix, strict=False))
            except ValueError:
                logger.warning("Invalid denied prefix in ACL config: %s", prefix)
        for host in acl.get("denied_hosts", []):
            try:
                self._denied_hosts.append(ip_address(host))
            except ValueError:
                logger.warning("Invalid denied host in ACL config: %s", host)
        min_pf = acl.get("min_prefix_length", {})
        self._min_prefix = {"ipv4": min_pf.get("ipv4", 8), "ipv6": min_pf.get("ipv6", 16)}
        max_pf = acl.get("max_prefix_length", {})
        self._max_prefix = {"ipv4": max_pf.get("ipv4", 32), "ipv6": max_pf.get("ipv6", 128)}

    def check_target(self, target: str) -> Optional[str]:
        """Returns None if allowed, error message string if denied."""
        if self._fail_closed:
            return "Query not allowed: ACL configuration unavailable"

        addr_str = target.split("/")[0]

        try:
            addr = ip_address(addr_str)
        except ValueError:
            return "Invalid IP address"

        for denied in self._denied_hosts:
            if addr == denied:
                return "Query not allowed for this target"

        for network in self._denied_networks:
            if addr in network:
                return "Query not allowed for this target"

        if "/" in target:
            try:
                net = ip_network(target, strict=False)
                version_key = "ipv4" if net.version == 4 else "ipv6"
                if net.prefixlen < self._min_prefix[version_key]:
                    return f"Prefix too broad. Minimum /{self._min_prefix[version_key]}"
                if net.prefixlen > self._max_prefix[version_key]:
                    return "Invalid prefix length"
            except ValueError:
                return "Invalid prefix"

        return None
