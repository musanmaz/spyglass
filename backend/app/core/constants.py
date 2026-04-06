SUPPORTED_QUERY_TYPES = {"bgp_route", "ping", "traceroute"}

SUPPORTED_PLATFORMS = {
    "cisco_xr", "cisco_iosxr", "juniper_junos", "cisco_ios", "cisco_nxos",
    "arista_eos", "huawei_vrp", "nokia_sros", "mikrotik",
    "frrouting", "bird", "openbgpd", "vyos", "tnsr",
}

PLATFORM_QUERY_SUPPORT = {
    "cisco_xr": {"bgp_route", "ping", "traceroute"},
    "cisco_iosxr": {"bgp_route", "bgp_community", "bgp_aspath", "ping", "traceroute"},
    "juniper_junos": {"bgp_route", "bgp_community", "bgp_aspath", "ping", "traceroute"},
    "cisco_ios": {"bgp_route", "bgp_community", "bgp_aspath", "ping", "traceroute"},
    "cisco_nxos": {"bgp_route", "bgp_community", "bgp_aspath", "ping", "traceroute"},
    "arista_eos": {"bgp_route", "bgp_community", "bgp_aspath", "ping", "traceroute"},
    "huawei_vrp": {"bgp_route", "bgp_community", "ping", "traceroute"},
    "nokia_sros": {"bgp_route", "bgp_community", "bgp_aspath", "ping", "traceroute"},
    "mikrotik": {"bgp_route", "ping", "traceroute"},
    "frrouting": {"bgp_route", "bgp_community", "bgp_aspath", "ping", "traceroute"},
    "bird": {"bgp_route", "bgp_community", "bgp_aspath"},
    "openbgpd": {"bgp_route", "bgp_community", "bgp_aspath"},
    "vyos": {"bgp_route", "ping", "traceroute"},
    "tnsr": {"bgp_route", "ping", "traceroute"},
}

DEVICE_ID_PATTERN = r"^[a-z0-9\-]+$"
