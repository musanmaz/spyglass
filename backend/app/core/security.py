import re
import ipaddress
from app.core.exceptions import SecurityError, TargetDeniedError

FORBIDDEN_PATTERNS = [
    r"[;&|`$]",
    r"\.\./",
    r"\\x[0-9a-fA-F]",
    r"\\u[0-9a-fA-F]",
    r"\n",
    r"\r",
    r"[\x00-\x1f]",
    r"(?i)(?:show|display|get|dump)\s+(?:run|start|config|tech|log|user|aaa|secret|password|key|crypto|certificate|snmp|community)",
    r"(?i)(?:configure|conf)\s+(?:terminal|t|exclusive|private|session)",
    r"(?i)(?:edit|set|delete|deactivate|activate|rollback|commit|load|save|write)",
    r"(?i)(?:system|undo|reset|reboot|reload|shutdown|halt|poweroff)",
    r"(?i)(?:copy|tftp|ftp|scp|sftp|wget|curl|fetch)",
    r"(?i)(?:telnet|ssh|rlogin|rsh)\s",
    r"(?i)(?:rm|del|erase|format|destroy|clear)\s",
    r"(?i)(?:debug|undebug|terminal\s+monitor)",
    r"(?i)(?:enable|disable|login|logout|exit|end|quit)\s*$",
    r"(?i)(?:bash|shell|start-shell|run\s+bash|request\s+system)",
    r"(?i)(?:file|more|dir|ls|cat|type|vi|nano|emacs)\s",
    r"(?i)(?:crypto|pki|key\s+generate|certificate)",
    r"(?i)(?:radius|tacacs|ldap|aaa)\s",
    r"(?i)(?:snmp-server|snmp\s+community)",
    r"(?i)(?:ip\s+route|ipv6\s+route|router|interface|vlan|vrf)\s",
    r"(?i)(?:access-list|prefix-list|route-map|policy)\s",
    r"(?i)(?:ntp|clock|logging|syslog|archive)\s",
    r"(?i)(?:username|password|secret|enable\s+secret)",
    r"(?i)(?:banner|hostname|domain-name)\s",
    r"(?i)(?:boot|upgrade|install|patch|package)\s",
    r"(?i)(?:license|feature|module)\s",
    r"(?i)(?:monitor|capture|packet-trace|ethanalyzer)\s",
    r"(?i)\|",
    r"(?i)(?:tee|redirect|append)\s",
    r"(?i)(?:alias|macro)\s",
    r"(?i)(?:event|applet|action|trigger)\s",
    r"(?i)(?:tcl|expect|python|ruby|perl|lua)\s",
    r"(?i)(?:source-interface|management)\s",
]

_compiled_forbidden = [re.compile(p) for p in FORBIDDEN_PATTERNS]

PRIVATE_NETWORKS = [
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("169.254.0.0/16"),
    ipaddress.ip_network("::1/128"),
    ipaddress.ip_network("fe80::/10"),
    ipaddress.ip_network("fc00::/7"),
    ipaddress.ip_network("100.64.0.0/10"),
]


def _check_forbidden_patterns(value: str) -> None:
    for pattern in _compiled_forbidden:
        if pattern.search(value):
            raise SecurityError("Forbidden character or command detected")


def validate_ip_or_prefix(target: str) -> str:
    _check_forbidden_patterns(target)

    try:
        network = ipaddress.ip_network(target, strict=False)
        addr = network.network_address
    except ValueError:
        try:
            addr = ipaddress.ip_address(target)
            network = ipaddress.ip_network(f"{addr}/{'32' if addr.version == 4 else '128'}")
        except ValueError:
            raise SecurityError("Invalid IP address or prefix")

    for private_net in PRIVATE_NETWORKS:
        if network.version == private_net.version and network.subnet_of(private_net):
            raise TargetDeniedError(target)

    if addr.is_multicast:
        raise TargetDeniedError(target)

    if addr.is_reserved:
        raise TargetDeniedError(target)

    if addr.is_unspecified:
        raise TargetDeniedError(target)

    return str(network) if "/" in target else str(addr)
