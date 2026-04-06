import pytest
from app.services.command_builder import CommandBuilder

class TestCommandBuilder:
    @pytest.fixture
    def builder(self):
        return CommandBuilder("config/commands.yaml")

    def test_cisco_iosxr_bgp_route_ipv4(self, builder):
        cmd = builder.build("cisco_iosxr", "bgp_route", "203.0.113.0/24", ip_version=4)
        assert cmd == "show bgp ipv4 unicast 203.0.113.0/24"

    def test_cisco_iosxr_ping(self, builder):
        cmd = builder.build("cisco_iosxr", "ping", "8.8.8.8", ip_version=4, source_ipv4="198.51.100.1")
        assert "ping ipv4 8.8.8.8" in cmd
        assert "source 198.51.100.1" in cmd

    def test_juniper_bgp_route(self, builder):
        cmd = builder.build("juniper_junos", "bgp_route", "8.8.8.0/24", ip_version=4)
        assert "show route 8.8.8.0/24" in cmd

    def test_unsupported_returns_none(self, builder):
        cmd = builder.build("mikrotik", "bgp_aspath", "^65000", ip_version=4)
        assert cmd is None

    def test_supported_queries(self, builder):
        queries = builder.get_supported_queries("cisco_iosxr")
        assert "bgp_route" in queries
        assert "ping" in queries
